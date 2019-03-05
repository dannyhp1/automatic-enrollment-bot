import urllib2
import urllib
import requests
from splinter import Browser
from selenium import webdriver
from bs4 import BeautifulSoup as bs

def get_login_url():
  base_url = "https://www.reg.uci.edu/cgi-bin/webreg-redirect.sh"
  file = urllib2.urlopen(base_url)
  content = file.read()
  soup = bs(content, 'html.parser')

  login_url = soup.find('meta').get('content')
  url_index_start = login_url.find('url') + 4
  login_url = login_url[url_index_start:]

  return login_url

def login(ucinetid, password):
  browser = Browser('chrome', incognito=True)
  browser.visit(get_login_url())
  browser.fill('ucinetid', ucinetid)
  browser.fill('password', password)
  browser.find_by_name('login_button').click()
  return browser

def enroll(browser, courses):
  print('Attempting to enroll in: ' + str(courses))
  success_courses = [ ]
  browser.find_by_value('Enrollment Menu').click()

  for i in range(len(courses)):
    browser.choose('mode', 'add')
    browser.fill('courseCode', courses[i])
    browser.find_by_value('Send Request').click()
    success_courses.append(courses[i])

  return success_courses

def get_information():
  file = open("user_information.txt")
  ucinetid = file.readline().strip()
  password = file.readline().strip()
  file.close()

  return [ucinetid, password]

def register_for_courses(courses):
  try:
    [ucinetid, password] = get_information()
    browser = login(ucinetid, password)
    successful_enrollment = enroll(browser, courses)
    print('Successfully enrolled in: ' + str(successful_enrollment))
    browser.find_by_value('Logout').click()
  
  except: 
    print('Errors have been thrown!')