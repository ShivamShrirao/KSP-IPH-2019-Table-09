from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random
    
class InstagramBot():
    def __init__(self, email, password):
        self.browserProfile = webdriver.ChromeOptions()
        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        self.browser = webdriver.Chrome('chromedriver.exe', chrome_options=self.browserProfile)
        self.email = email
        self.password = password
        
    def screenshot(self, username, count):
        self.browser.get('https://www.instagram.com/' + username)
        time.sleep(2)
        self.browser.execute_script("window.scrollTo(0, 1000)") 
        self.browser.save_screenshot("Instagram/"+str(count)+".png")

    def signIn(self):
        self.browser.get('https://www.instagram.com/accounts/login/')
        time.sleep(4)
        self.browser.find_element_by_xpath("//input[@name='username']").send_keys(self.email)
        passwordInput=self.browser.find_element_by_xpath("//input[@name='password']")
        passwordInput.send_keys(self.password)
        passwordInput.send_keys(Keys.ENTER)
        
        time.sleep(4)
    
    def getUserFollowers(self, username, max_lim):
        self.browser.get('https://www.instagram.com/' + username)
        followersLink = self.browser.find_element_by_css_selector('ul li a')
        followersLink.click()
        time.sleep(2)
        followersList = self.browser.find_element_by_css_selector('div[role=\'dialog\'] ul')
        numberOfFollowersInList = len(followersList.find_elements_by_css_selector('li'))
        followersList.click()
        actionChain = webdriver.ActionChains(self.browser)
        try:
            while (numberOfFollowersInList < max_lim):
                actionChain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
                time.sleep(random.randint(500,1000)/1000)
                numberOfFollowersInList = len(followersList.find_elements_by_css_selector('li'))
        
        except:
            pass
        
        followers = []
        try:
            for user in followersList.find_elements_by_css_selector('li'):
                userLink = user.find_element_by_css_selector('a').get_attribute('href')
                followers.append(userLink)
                if (len(followers) == max):
                    break
        except:
            pass
        return followers

    def closeBrowser(self):
        self.browser.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.closeBrowser()
