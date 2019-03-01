import time
import urllib2
from twilio.rest import Client
from bs4 import BeautifulSoup as bs
import pync
import register

def getCS161(twilio_sid, twilio_auth, twilio_phone, personal_phone, courses_to_enroll):
    url = "https://www.reg.uci.edu/perl/WebSoc?YearTerm=2019-14&CoCourse=34210"
    file = urllib2.urlopen(url)
    content = file.read()

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

    amount = len(cs161)
    lecture = cs161[0]

    lecture_code = lecture[0]
    lecture_open = int(lecture[2]) < int(lecture[3])
    lecture_status = lecture[4]
    discussion_open = False

    for i in range(1, amount):
        discussion_code = cs161[i][0]
        discussion_open = (int(cs161[i][2]) < int(cs161[i][3])) or cs161[i][4] != 'FULL'
        if(discussion_open):
            print("=====================================")
            print("Discussion is open ({d_code}) with lecture ({l_code}).".format(d_code = discussion_code, l_code = lecture_code))
            print("=====================================")
            pync.notify("Discussion is not full ({d_code}) with lecture ({l_code}).".format(d_code = discussion_code, l_code = lecture_code), 
                        open='https://www.reg.uci.edu/registrar/soc/webreg.html', title='CS 161')
            discussion_open = True            
            message = "Lecture ({l_code}) is {l_status}. Discussion ({d_code}) is {d_status}.".format(l_code = lecture_code, l_open = lecture_open, \
                                                                                                                l_status = lecture_status, d_code = discussion_code, \
                                                                                                                d_status = cs161[i][4])

            courses_to_enroll.append(discussion_code)
            courses_to_enroll.append(lecture_code)

            client = Client(twilio_sid, twilio_auth)

            message = client.messages \
                        .create(
                            body=message,
                            from_=twilio_phone,
                            to=personal_phone
                        )

            return

    if(discussion_open == False):
        print("No discussions were opened.")

def getCS145(twilio_sid, twilio_auth, twilio_phone, personal_phone, courses_to_enroll):
    url = "https://www.reg.uci.edu/perl/WebSoc?YearTerm=2019-1&CoCourse=34160"
    file = urllib2.urlopen(url)
    content = file.read()

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
    lecture_open = int(lecture[2]) < int(lecture[3])
    lecture_status = lecture[4]
    discussion_open = False

    for i in range(1, amount):
        discussion_code = cs145[i][0]
        discussion_open = (int(cs145[i][2]) < int(cs145[i][3])) or cs145[i][4] != 'FULL'
        if(discussion_open and i not in [1, 3, 5, 7]):
            print("=====================================")
            print("Discussion is not full ({d_code}) with lecture ({l_code}).".format(d_code = discussion_code, l_code = lecture_code))
            print("=====================================")
            pync.notify("Discussion is not full ({d_code}) with lecture ({l_code}).".format(d_code = discussion_code, l_code = lecture_code), 
                        open='https://www.reg.uci.edu/registrar/soc/webreg.html', title='CS 145')
            discussion_open = True
            message = "Lecture ({l_code}) is {l_status}. Discussion ({d_code}) is {d_status}.".format(l_code = lecture_code, l_open = lecture_open, \
                                                                                                                l_status = lecture_status, d_code = discussion_code, \
                                                                                                                d_status = cs145[i][4])

            courses_to_enroll.append(discussion_code)
            courses_to_enroll.append(lecture_code)

            client = Client(twilio_sid, twilio_auth)

            message = client.messages \
                        .create(
                            body=message,
                            from_=twilio_phone,
                            to=personal_phone
                        )

            return

    if(discussion_open == False):
        print("No discussions were opened.")

def get_information():
  file = open("twilio_information.txt")
  twilio_sid = file.readline().strip()
  twilio_auth = file.readline().strip()
  twilio_phone = file.readline().strip()
  personal_phone = file.readline().strip()
  file.close()

  return [twilio_sid, twilio_auth, twilio_phone, personal_phone]

if __name__ == "__main__":
    [twilio_sid, twilio_auth, twilio_phone, personal_phone] = get_information()

    while True:
        courses_to_enroll = [ ]
        print("Checking if discussion is open for CS 161...")
        getCS161(twilio_sid, twilio_auth, twilio_phone, personal_phone, courses_to_enroll)
        print("Checking if discussion is open for CS 145...")
        getCS145(twilio_sid, twilio_auth, twilio_phone, personal_phone, courses_to_enroll)

        if(len(courses_to_enroll) > 0):
            print("Enroll in: " + str(courses_to_enroll))
            register.register_for_courses(courses_to_enroll)

        time.sleep(5)
