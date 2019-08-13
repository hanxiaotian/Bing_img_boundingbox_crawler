from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import json
from urllib.request import Request, urlopen
import time

header = {'User-Agent':
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

def get_soup(url, header):
    return BeautifulSoup(urlopen(
        Request(url, headers=header)),
        'html.parser')

def wait_buttons(driver, name='', type=By.XPATH):
    timeout = 5
    if len(name) != 0:
        element_present = EC.element_to_be_clickable((type, name))
        WebDriverWait(driver, timeout).until(element_present)
    driver.implicitly_wait(timeout)

def scroll_down(driver):
    SCROLL_PAUSE_TIME = 1

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def main():
    query = 'dresses-cocktail'
    query = query.split()
    query = '+'.join(query)
    url = "http://www.bing.com/images/search?q=" + query + "&FORM=HDRSC2"

    # add the directory for image
    DIR = "data"

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome('./chromedriver', chrome_options=options)
    driver.maximize_window()

    driver.get(url)
    scroll_down(driver)

    soup = BeautifulSoup(driver.page_source, "lxml")
    print('total num of dresses: ', len(soup.find_all("a", {"class": "iusc"})))

    ActualImages = []

    for a in soup.find_all("a", {"class": "iusc"}):
        url = "http://www.bing.com" + a['href']

        driver.get(url)

        wait_buttons(driver, '//*[@id="actionbar"]/ul/li[1]/div')
        visual_seaerch_button = driver.find_element_by_xpath('//*[@id="actionbar"]/ul/li[1]/div')
        visual_seaerch_button.click()

        wait_buttons(driver, 'b_content', By.ID)
        img_soup = BeautifulSoup(driver.page_source, "lxml")
        sec = img_soup.find('div', {'class': 'imgContainer nofocus'})
        img_url = sec.find('img')['src']

        # wait_buttons(driver, 'core', By.CLASS_NAME)
        wait_buttons(driver)
        hotspots = driver.find_elements_by_class_name('core')
        print('num of hotspots: ', len(hotspots))
        if len(hotspots) == 0:
            continue

        boundingboxes = []
        img_size = []
        for idx in range(len(hotspots)):
            try:
                hotspots = driver.find_elements_by_class_name('core')
                hotspots[idx].click()
            except:
                continue
            print('click one hotspot')
            wait_buttons(driver)

            wait_buttons(driver, 'crop_rect', By.ID)
            sub_soup = BeautifulSoup(driver.page_source, "lxml")
            att = sub_soup.find("div", {"id": "crop_rect"})
            try:
                boundingbox = att['style']
                boundingboxes.append(boundingbox)
            except:
                continue

            img_size = driver.find_element(By.CSS_SELECTOR,
                                           '#mainImageWindow > div.mainImage.current > div > div > div > div')
            img_size = img_size.size

        ActualImages.append((img_url, img_size, boundingboxes))

    print("there are total", len(ActualImages), "images")

    driver.close()

    if not os.path.exists(DIR):
        os.mkdir(DIR)

    DIR = os.path.join(DIR, query.split()[0])
    if not os.path.exists(DIR):
        os.mkdir(DIR)

    # save images & bounding boxes
    with open(DIR + 'boundingbox.json', 'w') as label_file:
        for i, (url, img_size, boundingboxes) in enumerate(ActualImages):
            file_name = url.split('/')[-1]
            try:
                req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                raw_img = urlopen(req).read()
                f = open(os.path.join(DIR, file_name), 'wb')
                f.write(raw_img)
                f.close()

                data = dict()
                data[file_name] = boundingboxes
                data['size'] = img_size
                json.dump(data, label_file)
                label_file.write('\n')

            except Exception as e:
                print("could not load : " + url)
                print(e)

if __name__ == '__main__':
    main()
