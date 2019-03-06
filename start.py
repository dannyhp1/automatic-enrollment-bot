import time
import urllib2
from twilio.rest import Client
from bs4 import BeautifulSoup as bs
import enroll

cs161_url = "https://www.reg.uci.edu/perl/WebSoc?YearTerm=2019-14&CoCourse=34210"
cs145_url = "https://www.reg.uci.edu/perl/WebSoc?YearTerm=2019-1&CoCourse=34160"

def printNotification(discussion_code, lecture_code):
  print("Discussion ({d_code}) is open with lecture ({l_code}).".format(d_code = discussion_code, l_code = lecture_code))

def sendNotification(successful_courses):
  [twilio_sid, twilio_auth, twilio_phone, personal_phone] = get_information()
  
  message = ''

  if(len(successful_courses) > 0):
    message = 'Successfully enrolled in: {courses}'.format(courses = successful_courses)
  else:
    message = 'Failed to enroll in any courses. Program crashed.'

  client = Client(twilio_sid, twilio_auth)
  send_message = client.messages.create(body=message, from_=twilio_phone, to=personal_phone)


def get_information():
  file = open("twilio_information.txt")
  twilio_sid = file.readline().strip()
  twilio_auth = file.readline().strip()
  twilio_phone = file.readline().strip()
  personal_phone = file.readline().strip()
  file.close()

  return [twilio_sid, twilio_auth, twilio_phone, personal_phone]

def watchCS161(courses_to_enroll):
  file = urllib2.urlopen(cs161_url)
  content = file.read()
  file.close()

  soup = bs(content, 'html.parser')

  divs = soup.find_all('div')
  course_list = ''

  for div in divs:
      classes = div.get('class')
      if(classes != None):
          for item in div.get('class'):
              if(item == 'course-list'):
                  course_list = div

  rows = course_list.find_all('tr')
  cs161 = [ ]

  for row in rows:
      align = row.get('valign')
      if(align != None):
          code = ""
          class_type = ""
          max_enroll = -1
          enroll = -1
          status = ""

          max_columns = 0

          for i, td in enumerate(row.find_all('td')):
              if(i == 0):
                  code = td.getText()
              elif(i == 1):
                  class_type = td.getText()
              elif(i == 7):
                  max_enroll = td.getText()
              elif(i == 8):
                  enroll = td.getText()
              elif(i == 15):
                  status = td.getText()
              max_columns = i
          
          if(i >= 15):
              cs161.append([code, class_type, enroll, max_enroll, status])

  # cs161 now stores a list of lists (courses). The first item in the list is the lecture.
  amount = len(cs161)
  lecture = cs161[0]

  lecture_code = lecture[0]
  lecture_status = lecture[4] != 'FULL'
  
  discussion_open = False

  for i in range(1, amount):
    discussion_code = cs161[i][0]
    discussion_status = cs161[i][4] != 'FULL'
    if(discussion_status and lecture_status):
      printNotification(discussion_code, lecture_code)
      discussion_open = True            
      
      message = "CS 161 is open! Lecture ({l_code}) and discussion ({d_code}).".format(l_code = lecture_code, d_code = discussion_code)
      courses_to_enroll.append(discussion_code)
      courses_to_enroll.append(lecture_code)

      [twilio_sid, twilio_auth, twilio_phone, personal_phone] = get_information()
      client = Client(twilio_sid, twilio_auth)
      message = client.messages.create(body=message, from_=twilio_phone, to=personal_phone)

      return True

  if(discussion_open == False):
      print("No discussions were opened for CS 161.")

  return False

def watchCS145(courses_to_enroll):
  file = urllib2.urlopen(cs145_url)
  content = file.read()
  file.close()

  soup = bs(content, 'html.parser')

  divs = soup.find_all('div')
  course_list = ""

  for div in divs:
      classes = div.get('class')
      if(classes != None):
          for item in div.get('class'):
              if(item == 'course-list'):
                  course_list = div

  rows = course_list.find_all('tr')
  cs145 = [ ]

  for row in rows:
      align = row.get('valign')
      if(align != None):
          code = ""
          class_type = ""
          max_enroll = -1
          enroll = -1
          status = ""

          max_columns = 0

          for i, td in enumerate(row.find_all('td')):
              if(i == 0):
                  code = td.getText()
              elif(i == 1):
                  class_type = td.getText()
              elif(i == 7):
                  max_enroll = td.getText()
              elif(i == 8):
                  enroll = td.getText()
              elif(i == 15):
                  status = td.getText()
              max_columns = i
          
          if(i >= 15):
              cs145.append([code, class_type, enroll, max_enroll, status])

  amount = len(cs145)
  lecture = cs145[0]

  lecture_code = lecture[0]
  lecture_status = lecture[4] != 'FULL'

  discussion_open = False

  for i in range(1, amount):
      discussion_code = cs145[i][0]
      discussion_status = cs145[i][4] != 'FULL'
      if(discussion_status and lecture_status and i not in [1, 3, 5, 7]):
        printNotification(discussion_code, lecture_code)
        discussion_open = True
        
        message = "CS 145 is open! Lecture ({l_code}) and discussion ({d_code}).".format(l_code = lecture_code, d_code = discussion_code)
        courses_to_enroll.append(discussion_code)
        courses_to_enroll.append(lecture_code)

        [twilio_sid, twilio_auth, twilio_phone, personal_phone] = get_information()
        client = Client(twilio_sid, twilio_auth)
        message = client.messages.create(body=message, from_=twilio_phone, to=personal_phone)

        return True

  if(discussion_open == False):
      print("No discussions were opened for CS 145.")

  return False

if __name__ == '__main__':
  courses_to_enroll = [ ]

  cs161_enrolled = False
  cs145_enrolled = False  

  while(not cs161_enrolled or not cs145_enrolled):
    if(not cs161_enrolled):
      print('Checking for CS161...')
      cs161_enrolled = watchCS161(courses_to_enroll)

      if(len(courses_to_enroll) > 0):
        successfully_enroll = enroll.register_for_courses(courses_to_enroll)
        sendNotification(successfully_enroll)
        courses_to_enroll = [ ]
        time.sleep(10)

    if(not cs145_enrolled):
      print('Checking for CS145...')
      cs145_enrolled = watchCS145(courses_to_enroll)

      if(len(courses_to_enroll) > 0):
        successfully_enroll = enroll.register_for_courses(courses_to_enroll)
        sendNotification(successfully_enroll)
        courses_to_enroll = [ ]
        time.sleep(10)
    
    time.sleep(2.5)