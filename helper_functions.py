import requests
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import smtplib, ssl


def get_links(subject_name):
    header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0","Cookie": FBCOOKIE}
    htm = requests.get("https://www.facebook.com/search/people/?q="+subject_name,headers = header)
    profiles = list()
    for a in re.findall(r'<a title="[A-Za-z0-9 ]+" class="_32mo" .*?>',str(htm.content)) :
        profiles.append((a.split('"')[1], a.split('"')[5]))

    return profiles


def fetch_screen(name):
    profiles = get_links(name)[:5]

    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    chrome_options.add_argument("--headless") 


    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.maximize_window()
    print("Logging in....")
    driver.get("https://www.facebook.com/siddharth.mahajan.79")
    element = driver.find_element_by_id("email")
    element.send_keys(FBEMAIL)
    element = driver.find_element_by_id("pass")
    element.send_keys(FBPASS)
    element = driver.find_element_by_id("loginbutton")
    element.click()
    print("Logged in....")
    count = 1
    linkandpic = []
    for name,link in profiles:
        print("Fetching profile ",count)
        driver.get(link)
        driver.find_element_by_xpath("//*[@data-tab-key='photos']").click()
        driver.execute_script("window.scrollTo(0, 500)") 
        time.sleep(2)
        driver.save_screenshot("Screenshot/"+str(count)+".png")
        linkandpic.append((link,"Screenshot/"+str(count)+".png"))
        count +=1
    return linkandpic

def send_mail(password,target):
    obj = smtplib.SMTP('smtp-mail.outlook.com',587)
    obj.ehlo()
    obj.starttls()
    obj.login(EMAIL,password)
    from_add = EMAIL
    to_address = target
    subject = "Register for a course on OSINT"
    message="Click on the following link to register for the course: \n http://bit.ly/2QrMS8G"
    msg= "Subject: "+subject+'\n\n'+message
    obj.sendmail(from_add,to_address,msg)
