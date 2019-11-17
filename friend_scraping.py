import argparse, json, os, glob, time, sys, requests
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions
from datetime import datetime
import requests
import re
from requests_testadapter import Resp

def start_browser():
    #Setup browser
    print("Opening Browser...")
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--mute-audio")
    options.add_argument("--start-maximized")
    #options.add_argument("headless")
    options.add_experimental_option("prefs",{"profile.managed_default_content_settings.images":2})
    browser = Chrome(options=options)

    return browser

def sign_in(browser):
    #Sign in
    fb_start_page = 'https://m.facebook.com/'
    fb_user = FBEMAIL
    fb_pass = FBPASS
    print("Logging in %s automatically..." % fb_user)
    browser.get(fb_start_page)
    email_id = browser.find_element_by_id("m_login_email")
    pass_id = browser.find_element_by_id("m_login_password")
    email_id.send_keys(fb_user)
    pass_id.send_keys(fb_pass)
    pass_id.send_keys(u'\ue007')
    time.sleep(3)

def download_friends(url,browser):
    friends_html = "Friends/friends.html"
    url = list(url)
    url[10] = 'm'
    url.pop(8)
    url.pop(8)
    url = ''.join(url)
    browser.get(url)
    time.sleep(1)
    browser.execute_script("window.scrollTo(0, 300)") 
    browser.find_element_by_class_name("_7-1j").click()
    time.sleep(2)
    print('Scrolling to bottom...')
    #Scroll to bottom
    count = 0
    while browser.find_elements_by_css_selector('#m_more_friends') and count < 5:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        count+=1
        time.sleep(1)

    #Save friend list
    with open (friends_html, 'w', encoding="utf-8") as f:
        f.write(browser.page_source)
        print('%s) Downloaded' % friends_html)
        
class LocalFileAdapter(requests.adapters.HTTPAdapter):
    def build_response_from_file(self, request):
        file_path = request.url[7:]
        with open(file_path, 'rb') as file:
            buff = bytearray(os.path.getsize(file_path))
            file.readinto(buff)
            resp = Resp(buff)
            r = self.build_response(request, resp)

            return r

    def send(self, request, stream=False, timeout=None,
             verify=True, cert=None, proxies=None):

        return self.build_response_from_file(request)

def get_friends():
    '''
    Take friends from friends folder's dumped xml file
    '''
    requests_session = requests.session()
    requests_session.mount('file://', LocalFileAdapter())
    data = requests_session.get('file://C:/Users/Admin/Desktop/Friends/friends.html')

    fname_link = []
    for a in re.findall(r'<a href="/[A-Za-z0-9.=?]+">.*?</a>',str(data.content)) :
        a = a.split('"')
        name = a[2].split("<")[0][1:]
        link = "https://www.facebook.com"+a[1]
        fname_link.append((name,link))
    return fname_link


def get_information(profile_link,driver):
    username=profile_link.split("facebook.com/")[1]
    print("Username:",username)
    sections = {
        'photo_url': {'src':'//div[@id="objects_container"]//a/img[@alt][1]'},
        'tagline': {'txt':'//*[@id="root"]/div[1]/div[1]/div[2]/div[2]'},
        'about': {'txt':'//div[@id="bio"]/div/div[2]/div'},
        'quotes': {'txt':'//*[@id="quote"]/div/div[2]/div'},
        'rel': {'txt':'//div[@id="relationship"]/div/div[2]'},
        'rel_partner': {'href':'//div[@id="relationship"]/div/div[2]//a'},
        'details': {'table':'(//div[2]/div//div[@title]//'},
        'work': {'workedu':'//*[@id="work"]/div[1]/div[2]/div'},
        'education': {'workedu':'//*[@id="education"]/div[1]/div[2]/div'},
        'family': {'fam':'//*[@id="family"]/div/div[2]/div'},
        'life_events': {'years':'(//div[@id="year-overviews"]/div[1]/div[2]/div[1]/div/div[1])'}
    }
    driver.get("https://mbasic.facebook.com/"+username+"/about")
    name=driver.find_element_by_xpath('/html/body/div/div/div[2]/div/div[1]/div[1]/div[2]/div[1]/span/div/span/strong')
    d = {'name': name.text}
    x = driver.find_element_by_xpath
    xs = driver.find_elements_by_xpath
    for k,v in sections.items():
        try:
            if 'src' in v:
                d[str(k)] = x(v['src']).get_attribute('src')
            elif 'txt' in v:
                d[str(k)] = x(v['txt']).text
            elif 'href' in v:
                d[str(k)] = x(v['href']).get_attribute('href')[8:].split('?')[0]
            elif 'table' in v:
                d['details'] = []
                rows = xs(v['table']+'td[1])')
                for i in range (1, len(rows)+1):
                    deets_key = x(v['table']+'td[1])'+'['+str(i)+']').text
                    deets_val = x(v['table']+'td[2])'+'['+str(i)+']').text
                    d['details'].append({deets_key:deets_val})
            elif 'workedu' in v:
                d[str(k)] = []
                base = v['workedu']
                rows = xs(base)
                for i in range (1, len(rows)+1):
                    dd = {}
                    dd['link'] = x(base+'['+str(i)+']'+'/div/div[1]//a').get_attribute('href')[8:].split('&')[0].split('/')[0]
                    dd['org'] = x(base+'['+str(i)+']'+'/div/div[1]//a').text
                    dd['lines'] = []
                    lines = xs(base+'['+str(i)+']'+'/div/div[1]/div')
                    for l in range (2, len(lines)+1):
                        line = x(base+'['+str(i)+']'+'/div/div[1]/div'+'['+str(l)+']').text
                        dd['lines'].append(line)
                    d[str(k)].append(dd)
            elif 'fam' in v:
                d[str(k)] = []
                base = v['fam']
                rows = xs(base)
                for i in range (1, len(rows)+1):
                    d[str(k)].append({
                        'name': x(base+'['+str(i)+']'+'//h3[1]').text,
                        'rel': x(base+'['+str(i)+']'+'//h3[2]').text,
                        'alias': x(base+'['+str(i)+']'+'//h3[1]/a').get_attribute('href')[8:].split('?')[0]
                    })
            elif 'life_events' in k:
                d[str(k)] = []
                base = v['years']
                years = xs(base)
                for i in range (1,len(years)+1):
                    year = x(base+'['+str(i)+']'+'/div[1]').text
                    events = xs(base+'['+str(i)+']'+'/div/div/a')
                    for e in range(1,len(events)+1):
                        event = x('('+base+'['+str(i)+']'+'/div/div/a)'+'['+str(e)+']')
                        d[str(k)].append({
                            'year': year,
                            'title': event.text,
                            'link': event.get_attribute('href')[8:].split('refid')[0]
                        })
        except Exception:
            pass
    for key in d.keys():
        print(key.upper(),": ",end="")
        if type(d[key]) is list:
            print("\n",end="")
            for itm in d[key]:
                if type(itm) is dict:
                    for kff in itm.keys():
                        print("\t",kff.upper(),":",itm[kff])
        else:
            print(d[key])
