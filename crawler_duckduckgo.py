from unicodedata import name
import pandas as pd
import os
import requests
from tqdm import tqdm
import shutil
import argparse
import time
from pygments import highlight
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException, StaleElementReferenceException
import platform
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
# from sympy import ImageSet
from webdriver_manager.chrome import ChromeDriverManager
import os.path as osp


def make_dir(keyword):

    current_path = os.getcwd()
    path = os.path.join(current_path, keyword)
    if not os.path.exists(path):
        os.mkdir(path)
        return 0
    else:
        return len([name for name in os.listdir(path) if os.path.isfile(name)])


def download(filename, link):
    try:
        response = requests.get(link, stream=True, timeout=5)
    except:
        return
    file_size = int(response.headers.get('content-length', 0))

    progress = tqdm(response.iter_content(chunk_size=1024),
                    f"Downloading {filename}", total=file_size, unit='B', unit_scale=True, unit_divisor=1024)
    print(f"Download file {filename}")
    with open(filename, 'wb') as f:
        # shutil.copyfileobj(response.raw, f)
        for data in progress:
            f.write(data)
            progress.update(len(data))


def search(keyword, data):
    keys = keyword.split(" ")[1:-1]
    key = ''
    for i in keys:
        key += i
    folder = os.path.join('data', key)
    # create folder if not exist
    n = make_dir(folder)
    # translate english to data['language]
    trans = crawler.translate(data['language'], keyword)
    # collect links
    links = data['search_engine'](trans)

    # download images
    for idx, link in enumerate(links):
        filename = "{}.png".format(str(n+idx))
        download(os.path.join(folder, filename), link)


class ChromeCrawler:
    def __init__(self, no_gui=False, proxy=None):
        executable = None
        # chose driver
        if platform.system() == 'Windows':
            print("Detected OS : Windows")
            executable = 'chromedriver.exe'
        elif platform.system() == 'Linux':
            print("Detect OS : Linux")
            executable = './chromedriver/chromedriver_linux'
        elif platform.system() == "Darwin":
            print("Detected OS : Mac")
            executable = './chromedirver/chromedirver_mac'
        else:
            raise OSError("Unknow OS Type")

        if not osp.exists(executable):
            raise FileNotFoundError(
                f"Chromedriver file should be placed at {executable}")

        # Chrome config
        chrome_option = Options()
        chrome_option.add_argument('--no-sandbox')
        chrome_option.add_argument('--disable-dev-shm-usage')
        if no_gui:
            chrome_option.add_argument('--headless')
        if proxy:
            chrome_option.add_argument("--proxy-server={}".format(proxy))

        # Install browser
        self.browser = webdriver.Chrome(
            ChromeDriverManager().install(), options=chrome_option)

        # print config browser
        browser_version = 'Failed to detect version'
        chromedriver_version = 'Failed to detect version'
        major_version_different = False

        if 'browserVersion' in self.browser.capabilities:
            browser_version = str(self.browser.capabilities['browserVersion'])

        if 'chrome' in self.browser.capabilities:
            if 'chromedriverVersion' in self.browser.capabilities['chrome']:
                chromedriver_version = str(
                    self.browser.capabilities['chrome']['chromedriverVersion'])

        if browser_version.split('.')[0] != chromedriver_version.split('.')[0]:
            major_version_different = True

        print('__________________________')
        print(f'Current web-browser version:\t{browser_version}')
        print(f'Current chrome-driver version:\t{chromedriver_version}')
        if major_version_different:
            print('Warning: Version different')
            print('http://chromedriver.chromium.org/downloads')

    def click(self, xpath):
        w = WebDriverWait(self.browser, 15)
        elem = w.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        elem.click()

    def google(self, keyword):
        # get into page
        self.browser.get(
            'https://duckduckgo.com/?q={}&t=h_&iax=images&ia=images'.format(keyword))

        WebDriverWait(self.browser, timeout=15).until(
            lambda x: x.find_element(By.TAG_NAME, "body"))

        print('Scrolling down')

        elem = self.browser.find_element(By.TAG_NAME, "body")

        for i in range(30):
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)

        print("finish scrolling")

        photos = self.browser.find_elements(
            By.XPATH, '//div[@class="tile--img__media"]')
        
        self.click('//div[@class="tile--img__media"]')
        
        links = []

        for i in range(200):
            img = elem.find_element(By.XPATH,"div[2]/div[3]/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div/a")
            src = img.get_attribute('href')
            links.append(src)
            elem.send_keys(Keys.ARROW_RIGHT)
            
        return links

if __name__ == "__main__":
    data = pd.read_csv('keywords.csv')
    for i in range(len(data)):
        key = data.keyword.iloc[i]+" Gemstone"
        folder = os.path.join('data\\',key)
        if os.path.exists(folder):
            continue
        os.mkdir(folder)
        crawler = ChromeCrawler()
        links=crawler.google(key)
        crawler.browser.close()
        for i in range(len(links)):
            try:
                download(folder+'\\'+str(i)+".png", links[i])
            except:
                continue
