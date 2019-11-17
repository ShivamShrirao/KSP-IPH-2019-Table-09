#!/usr/bin/env python3
import face_utils
import requests
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from requests_testadapter import Resp
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions
import importlib
import os

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


    
def get_links(subject_name):
    header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0","Cookie": 'sb=ufgMXRKi5bcIfSSMaIelRh5G; datr=ufgMXdM8hrLb-psr4lJbZwMo; c_user=100004912332911; xs=33%3AnSUFMmc3rtO1kg%3A2%3A1569653696%3A15717%3A8272; spin=r.1001436623_b.trunk_t.1573795693_s.1_v.2_; fr=0WfA239LUIWQj54ZH.AWX55JfOK3_vBs2e71NqKaucnlE.Bc8pR5.Ea.AAA.0.0.Bdz4xe.AWVLIfVN; presence=EDvF3EtimeF1573883961EuserFA21B04912332911A2EstateFDt3F_5bDiFA2user_3a1B07388262849A2EoF1EfF1C_5dEutc3F1573730942948G573883961180CEchFDp_5f1B04912332911F1CC; wd=616x657; act=1573884013894%2F10'}
    htm = requests.get("https://www.facebook.com/search/people/?q="+subject_name,headers = header)
    profiles = list()
    for a in re.findall(r'<a title="[A-Za-z0-9 ]+" class="_32mo" .*?>',str(htm.content)) :
        profiles.append((a.split('"')[1], a.split('"')[5]))

    return profiles

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)
chrome_options.add_argument("--headless")
driver = webdriver.Chrome("/home/archer/Documents/OSINT_India_Police_Hackathon/chromedriver",chrome_options=chrome_options)
# driver.maximize_window()
print("Logging in....")
driver.get("https://www.facebook.com/siddharth.mahajan.79")
element = driver.find_element_by_id("email")
element.send_keys(FBEMAIL)
element = driver.find_element_by_id("pass")
element.send_keys(FBPASS)
element = driver.find_element_by_id("loginbutton")
element.click()
print("Logged in....")

def fetch_screen(name):
    profiles = get_links(name)[:5]
    count = 1
    linkandpic = []
    for name,link in profiles:
        print("Fetching profile ",count)
        driver.get(link)
        driver.find_element_by_xpath("//*[@data-tab-key='photos']").click()
        imct=1
        driver.execute_script("window.scrollTo(0, 500)")
        linkandpic.append([link,[]])
        while imct<=2:
            time.sleep(2.5)
            fname="Screenshot/"+str(count)+"_"+str(imct)+".png"
            driver.save_screenshot(fname)
            linkandpic[-1][1].append(fname)
            driver.execute_script("window.scrollTo(500,1000)")
            imct+=1
        count +=1
    return linkandpic

def validate_profile(name,image):
    lnpc=fetch_screen(name)
    recs=[]
    for i in lnpc:
        recs.append(i[1])
    print("Recognising and counting targets.")
    pidx=face_utils.count_targets(image,recs)
    profile_link=lnpc[pidx][0].split("?ref")[0]
    return profile_link
    
    

def download_friends(url):
    friends_html = "Friends/friends.html"
    url = list(url)
    url[10] = 'm'
    url.pop(8)
    url.pop(8)
    url = ''.join(url)
    driver.get(url)
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, 300)") 
    driver.find_element_by_class_name("_7-1j").click()
    time.sleep(2)
    print('Scrolling to bottom...')
    #Scroll to bottom
    count = 0
    while driver.find_elements_by_css_selector('#m_more_friends') and count < 5:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        count+=1
        time.sleep(1)

    #Save friend list
    with open (friends_html, 'w', encoding="utf-8") as f:
        f.write(driver.page_source)
        print('%s) Downloaded' % friends_html)
        
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

def get_information(profile_link):
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
    info_str = ""
    for key in d.keys():
        info_str = info_str + key.upper()+": "
        if type(d[key]) is list:
            info_str += "\n"
            for itm in d[key]:
                if type(itm) is dict:
                    for kff in itm.keys():
                        info_str = info_str + "\t"+kff.upper()+": "+str(itm[kff])+"\n"
        else:
            info_str = info_str + d[key]+"\n"
    return info_str

