import pandas as pd
import numpy as np
import smtplib
import bs4
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# # Setting browser
# Setting browser's options
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--start-maximized")
options.add_argument("--disable-popup-blocking")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(0)
print("-- Driver setup and browser opened")

# Access link
sleep(1)
driver.get('https://glints.com/vn/opportunities/jobs/explore')
print('-- Glints accessed')

# # Surpass website's noti
# Scroll page to pop up the message
sleep(7)
html = driver.find_element(By.TAG_NAME,'html')
html.send_keys(Keys.DOWN)

# Escape
sleep(5)
html.send_keys(Keys.ESCAPE)


# # INFORMATION REQUIRED TO RUN PROGRAM 
# - Search keyword
# - Sender email
# - Sender gmail app password: get from gmail
# - Reciever gmail

def search_keyword(keyword):
    search_box = driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[3]/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div/input')
    sleep(1)
    search_box.send_keys(Keys.CONTROL + "a")
    search_box.send_keys(Keys.DELETE)
    search_box.send_keys(keyword)
    sleep(1.5)
    # CHANGE XPATH
    # search_button = driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[4]/div[2]/div[2]/div[2]/div[2]/div/div/div[3]/button')
    search_button = driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[3]/div[2]/div[2]/div[2]/div[2]/div/div/div[3]/button')
    search_button.click()

while True:
    keyword = input('-- Search keyword: ')
    
    # Input keyword and search
    search_keyword(keyword)
    sleep(4)
    # get page source
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="MainContainersc__MainBody-sc-iy5ixg-2 dyvvBG"]')))
    html_of_interest = driver.execute_script('return arguments[0].innerHTML',element)
    soup = BeautifulSoup(html_of_interest, 'lxml')

    
    jobcnt = soup.select('h1[class="ExploreTabsc__JobCount-sc-gs9c0s-4 iAPXyD"]')
    try:
        jobcnt = int(jobcnt[0].text.split(' ',1)[0]) 

        if jobcnt != 0:
            answer = input(f'-- {jobcnt} jobs found in Vietnam, do you want to begin the scraper? (y/n)  ')
            if answer.lower().startswith("y"):
                print(f'-- Keyword confirmed: {keyword}')
                break
            else: 
                print('-- Please choose another keyword')
                continue
        else:
            print('-- No job found, please choose another keyword')
            continue 
    except:
        print('-- No job found, choose another keyword ')
        continue 

hidden_answer = True 
while True:
    answer_email = input('-- Do you want to recieve notifications by email? (y/n)  ')
    if answer_email.lower().startswith("y"):
        while True:
            sender_gmail = input('-- Sender gmail: ')
            sender_apppass = input('-- Sender gmail app password: ')
            reciever = input('-- Reciever gmail: ')
            subject = '-- Glints Data Scrape'

            def sendemail(sender_gmail, sender_apppass, reciever, subject, message):
                server = smtplib.SMTP('smtp.gmail.com',587)
                server.ehlo()
                server.starttls()
                                                
                server.login(sender_gmail,sender_apppass)
                server.sendmail(sender_gmail, reciever,f'Subject: {subject}\n{message}')
                server.quit()
                print('-- Email setup successfully') 
            message = 'Glints data scraping program initialized successfully'
            try:
                sendemail(sender_gmail, sender_apppass, reciever, subject, message)
                break
            except:
                print('-- Fail to send email, please check inputs')
                continue
        break 
    elif answer_email.lower().startswith("n"): 
        hidden_answer = False 
        break 
    else:
        continue 

# Refresh page to start scrolling
driver.refresh()
sleep(7)
html = driver.find_element(By.TAG_NAME,'html')
html.send_keys(Keys.DOWN)

# Escape
sleep(5)
html.send_keys(Keys.ESCAPE)

# # Roll page to open all list views
print('-- Loading pages to get detail urls')
while True:
    page_height = driver.execute_script("return document.body.scrollHeight")
    target_height = page_height - 1220
    driver.execute_script("window.scrollTo(0, %s);" %target_height )
    sleep(2)
    try:
        state = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[3]/div[2]/div[2]/div[2]/div[4]/div[2]/div[2]/span')
        if state.text == 'Đã tải lên tất cả cơ hội việc làm':
            print('-- All page loaded')
            # Noti
            if hidden_answer == True:
                message = ('All page loaded, ready to extract urls')
                sendemail(sender_gmail, sender_apppass, reciever, subject, message)
            break 
    except:
        continue 
# # Extract url of detail views
# get page source
element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="MainContainersc__MainBody-sc-iy5ixg-2 dyvvBG"]')))
html_of_interest = driver.execute_script('return arguments[0].innerHTML',element)
soup = BeautifulSoup(html_of_interest, 'lxml')

#  pull all posts with beautifulsoup
posts = soup.select('div[class="JobCardsc__JobCardWrapper-sc-1f9hdu8-1 dPPDau"]>a')

# append all urls to detail_urls
detail_urls = []
for post in posts:
    detail_urls.append('https://glints.com' + post['href'])
print(f'-- Total urls extracted: {len(detail_urls)}')

# save the list into a df and extract it as a file
df = pd.DataFrame({'Detail Urls':detail_urls})
df.to_csv('detail_urls.csv')
print('-- Detail urls saved to file detail_urls.csv')
sleep(5)
# # Extract data from detail views

# Extract data function
# FUNCTION
def extract(link):
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="GlintsContainer-sc-ap1z3q-0 iUnyrV"]')))
    html_of_interest = driver.execute_script('return arguments[0].innerHTML',element)
    soup = BeautifulSoup(html_of_interest, 'lxml')

    item_dict = {}

    # Company Name
    try:
        item_dict['Name'] = soup.select('div[class="TopFoldsc__JobOverviewHeader-sc-kklg8i-22 ihxBLZ"]')[0].text
    except:
        item_dict['Name'] = None 

    # Company Name
    try:
        item_dict['Company'] = soup.select('div[class="TopFoldsc__JobOverViewCompanyName-sc-kklg8i-5 eLQvRY"]>a')[0].text
    except:
        item_dict['Company'] = None 

    # Location
    try:
        item_dict['Location'] = soup.select('div[class="TopFoldsc__JobOverViewCompanyLocation-sc-kklg8i-6 gLATOW"]>span>a')[0].text
    except:
        item_dict['Location'] = None 


    # Salary range 
    try:
        salary_ele = soup.select('div[class="TopFoldsc__JobOverViewInfoContainer-sc-kklg8i-8 fgSCsF"]>div>span')[0]
        salary_txt = salary_ele.text 
        item_dict['Salary'] = salary_txt
    except:
        item_dict['Salary'] = None 


    # Experienc, Type, Field`
    info = soup.select('div[class="TopFoldsc__JobOverViewInfo-sc-kklg8i-9 EWOdY"]')
    info_list = []
    for ite in info:
        info_list.append(ite.text)

    item_dict['Experience'] = None
    item_dict['Type'] = None 

    for ele in info_list:
        if 'kinh nghiệm' in ele:
            item_dict['Experience'] = ele 
            info_list.remove(ele)
    for ele in info_list:  
        if ('Việc' in ele) or ('Thực Tập' in ele):
            item_dict['Type'] = ele
            info_list.remove(ele)
    try:
        item_dict['Field'] = info_list[0]
    except:
        item_dict['Field'] = None

    # Posted and Updated time
    try:
        posted = soup.select('span[class="TopFoldsc__PostedAt-sc-kklg8i-11 eRKLIR"]')
        posted = posted[0].text.split(' ',1)[1]
        item_dict['Posted'] = posted
    except:
        item_dict['Posted'] = None

    try:
        updated = soup.select('span[class="TopFoldsc__UpdatedAt-sc-kklg8i-12 bYndtI"]')
        updated = updated[0].text.split(' ',1)[1]
        item_dict['Updated'] = updated
    except:
        item_dict['Updated'] = None

    #  Skill required
    try:
        skills = soup.select('div[class="TagStyle__TagContainer-sc-66xi2f-1 gtZZMG aries-tag Skillssc__TagOverride-sc-11imayw-3 fyJqX"]')
        skills_str = ''
        for i in range(len(skills)):
            if i == (len(skills) -1 ):
                sub = skills[i].text
            else:
                sub = skills[i].text + ', '
            skills_str = skills_str + sub
        item_dict['Skill Required'] = skills_str
    except:
        item_dict['Skill Required'] = None 

    # Link
    try:
        item_dict['Link'] = link
    except:
        item_dict['Link'] = None 
    df_list.append(item_dict)

# Import url from detail_urls
#  import urls from the file
urls = pd.read_csv('detail_urls.csv')
urls = urls['Detail Urls']

# Begin to scrap data
print(f'-- URL count: {len(urls)}, estimated time: {len(urls)*5}s')
print('-- Progress:',end= ' ')
sleep_time = 5
try:
    cnt = 0
    df_list = []
    total_urls = len(urls)

    # Loop through detail_urls to get link
    for link in urls.iloc:
        driver.get(link)
        sleep(sleep_time)
        try: 
            extract(link)
        except Exception as e:
            print(f'-- Error raised: {e.__class__} ,at url number {cnt}. Passed to the next url')
            continue
            
        cnt += 1
        # PROGRESS ANNOUNCEMENT
        if cnt%10 == 0:
            print(f'{round((cnt/total_urls)*100,3)}%', end=' --> ')

    # Notification
    print(f'-- Successfully scraped all data!!')

    if hidden_answer == True:
        message = f'Successfully scraped all data!!\nTotal data records: {len(df_list)}\nTotal urls: {len(urls)}'
        sendemail(sender_gmail, sender_apppass, reciever, subject, message)

except Exception as err:
    print(f'-- Program shut down at url number {cnt}. Error: {err.__class__}')

    #  Notification
    if hidden_answer == True:
        message = f'Error raised at url number {cnt}, program stopped\nData saved\nTotal urls: {len(urls)}'
        sendemail(sender_gmail, sender_apppass, reciever, subject, message)

finally:
    # Save df to data file named ScrapedData
    df = pd.DataFrame(df_list)
    df.to_csv('ScrapedData.csv')

