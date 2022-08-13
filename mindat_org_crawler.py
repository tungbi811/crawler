import cloudscraper
import re
import requests 
from bs4 import BeautifulSoup as bs
import time
import random
from tqdm import tqdm
import webbrowser
import pyautogui
import os

def get_src(tag):
    tag = str(tag)
    src_pos = tag.find('src')
    return 'https://www.mindat.org/'+tag[src_pos+5:-3]

def get_name(tag):
    tag = str(tag)
    content_pos = tag.find('content')
    return tag[content_pos+9:-3]

def fix_name_window(name):
    name = name.replace('/','')
    name = name.replace('\\','')
    name = name.replace(':','-')
    name = name.replace('*','')
    name = name.replace('?','')
    name = name.replace('>','')
    name = name.replace('<','')
    name = name.replace('|','')
    return name

def fix_name_ubuntu(name):
    name = name.replace('/','')
    name = name.replace('\\','')
    return name

def verify():
    url = 'https://www.mindat.org/'

    chrome_path = '/usr/bin/google-chrome %s'

    webbrowser.get(chrome_path).open_new(url)

    time.sleep(10)

    # Presses the tab key once
    pyautogui.press("tab")
    pyautogui.press("enter")
    time.sleep(2)
    pyautogui.press("tab")
    pyautogui.press("tab")
    pyautogui.press("tab")
    pyautogui.press("enter")
    time.sleep(4)
    pyautogui.hotkey('ctrl', 'w')
    time.sleep(1)
    pyautogui.hotkey('alt', 'tab')

def download(filename,link):
    try:
        response = requests.get(link, stream=True,timeout=10)
    except:
        return
    file_size = int(response.headers.get('content-length', 0))
    filename = str(i)+'-'+filename
    progress = tqdm(response.iter_content(chunk_size=1024), f"Downloading {filename}", total=file_size, unit='B', unit_scale=True, unit_divisor=1024)
    print(f"Download file {filename}")
    with open('data/'+filename+src[-4:],'wb') as handler:
        for data in progress:
            handler.write(data)
            progress.update(len(data))

tik = time.ctime()
index = [i for i in range(74265,75000)]
while index!=[]:
    i = index[0]
    print(i)
    for j in range(10):
        scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
        try:
            page = scraper.get(f"https://www.mindat.org/photo-{i}.html",timeout=30).text
        except:
            break
        if page.count('img')>3:
            tag_src = re.findall('<img id="mainphoto" src=".*"',page)
            scraper.close()
            if tag_src == []:
                index.pop(0)
                break
            src = get_src(tag_src)
            tag_name = re.findall('<meta property="og:title" content=".*"',page)
            label = fix_name_ubuntu(get_name(tag_name))
            download(label,src)
            index.pop(0)
            break
        if j==9:
            print('\a')
            print('----------------------------------------')
            print('Checking again')
            print('----------------------------------------')
            # verify()
            # check = input("Done [y/n]: ")
        # time.sleep(random.randrange(1,2))
tok = time.ctime()
print(tik)
print(tok)