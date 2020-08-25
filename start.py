import time
from urllib.request import urlopen
from twilio.rest import Client
from bs4 import BeautifulSoup as bs
import enroll

# Base URL for UCI's schedule of classes.
webreg_base = 'https://www.reg.uci.edu/perl/WebSoc?YearTerm={year}{quarter}&ShowComments=on&ShowFinals=on&Breadth=ANY&Dept={dept}&CourseNum={course_number}&Division=ANY&CourseCodes=&InstrName=&CourseTitle=&ClassType=ALL&Units=&Days=&StartTime=&EndTime=&MaxCap=&FullCourses=ANY&FontSize=100&CancelledCourses=Exclude&Bldg=&Room='
fall_quarter = '-92'
winter_quarter = '-03'
spring_quarter = '-14'

def sendErrorNotification(message):
  [twilio_sid, twilio_auth, twilio_phone, personal_phone] = get_information()

  client = Client(twilio_sid, twilio_auth)
  send_message = client.messages.create(body=message, from_=twilio_phone, to=personal_phone)

def sendNotification(successful_enroll, successful_waitlist):
  [twilio_sid, twilio_auth, twilio_phone, personal_phone] = get_information()
  
  message = 'Successfully enrolled in: {enroll}, waitlisted in: {waitlist}'.format(enroll = successful_enroll, waitlist = successful_waitlist)

  client = Client(twilio_sid, twilio_auth)
  send_message = client.messages.create(body=message, from_=twilio_phone, to=personal_phone)


def get_information():
  # Store twilio authentication information and personal number in a file.
  file = open("twilio_information.txt")
  twilio_sid = file.readline().strip()
  twilio_auth = file.readline().strip()
  twilio_phone = file.readline().strip()
  personal_phone = file.readline().strip()
  file.close()

  return [twilio_sid, twilio_auth, twilio_phone, personal_phone]

def parse_course(year, quarter, dept, course_number):
  # Course dept. needs to be reparsed due to json data.
  parsed_dept = dept.replace(' ', '%20') if dept != None else None
  course_url = webreg_base.format(year=year, quarter=quarter, dept=parsed_dept, course_number=course_number)
  
  page = urlopen(course_url)
  content = page.read()
  page.close()

  # Create a bs object for the content.
  soup = bs(content, 'html.parser')

  table_rows = soup.find_all('tr')
  valid_rows = [ ]

  # On webreg, the course info is within tables and have valign = top.
  for row in table_rows:
      valign = row.get('valign')
      if(valign != None and valign == 'top'):
          valid_rows.append(row)

  # There will be no table shown if the course does not exist or is not available.
  if(len(valid_rows) <= 0):
      return None, [ ]

  # The row in the table consists of the course information.
  course_information = valid_rows[0]
  course_name = None

  for td in course_information.find_all('td'):
      if('CourseTitle' in td.get('class')):
          course_name = td.getText()
  
  course_list = valid_rows[1:]
  courses = [ ]

  # Iterate through all the remaining rows to get information.
  for course in course_list:
      course_information = [ ]
      
      for i, td in enumerate(course.find_all('td')):
          if(i == 0 or i == 1 or i == 4 or i == 5 or i == 8 or i == 13 or i == 16):
              # 0 = course code, 1 = course type, 4 = instructor, 8 = maximum, 9 = enrolled, 16 = status.
              course_information.append(td.getText())
          elif(i == 9):
              # Current availability may differ if sections are crossed.
              text = td.getText().split(' ')
              course_information.append(text[-1])

      courses.append(course_information)

  # All of the valid courses should have 6 attributes (listed above).
  courses = [course for course in courses if len(course) == 8]

  return course_name, courses

# This method is simply for an example to validate a course (CS 161 in this case).
def validate_cs161(sections, enroll, waitlist):
  # You can also check if courses are restricted and such in this validation method.
  lecture = sections[0]
  discussions = sections[1:]

  # Should only add lecture/discussion if lecture is not full.
  if(lecture[7].strip() != 'FULL'):
    if(lecture[7].strip() == 'OPEN'):
      # Lecture is OPEN.
      for discussion in discussions:
        if(discussion[7].strip() == 'OPEN'):
          enroll.append(lecture[0])
          enroll.append(discussion[0])
          return
    else:
      # Lecture is WAITL.
      for discussion in discussions:
        if(discussion[7].strip() == 'Waitl'):
          waitlist.append(lecture[0])
          waitlist.append(discussion[0])
          return

  return

if __name__ == '__main__':
  try:
    enroll_courses = [ ]
    waitlist_courses = [ ]

    enrolled = False

    while(not enrolled):
      print('Automatic enrollment in process...')

      # Get list of all courses.
      # e.g. CS 161 for Winter 2020:
      cs161 = parse_course('2020', winter_quarter, 'COMPSCI', '161')[1]

      # Create a validation method that will check if the lecture/discussion is open for enrollment.
      # Pass in enroll_courses and waitlist_courses; method should append into these lists if section is open.
      validate_cs161(cs161, enroll_courses, waitlist_courses)

      if(len(enroll_courses) >= 1 or len(waitlist_courses) >= 1):
        enrolled = True

        # Attempt to enroll and waitlist in courses.
        success_enroll, success_waitlist = enroll.register_for_courses(enroll_courses, waitlist_courses)
        if(len(success_enroll) == 0 and len(success_waitlist) == 0):
          sendErrorNotification('Failed to enroll in: ' + str(enroll_courses) + ', and failed to waitlist in: ' + str(waitlist_courses))
        else:
          sendNotification(success_enroll, success_waitlist)

      # Set the time: how many seconds between each time the bot checks the enrollment.
      time.sleep(10)
  except Exception as e:
    sendErrorNotification('Automatic enrollment has crashed with exception: ' + e)
