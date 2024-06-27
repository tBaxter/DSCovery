import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.utils.timezone import make_aware
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
BLOCK_LIST = ["Oracle", "Canonical"]


def scroll_to_bottom(driver,sleep_time=200):
    """
    Helper function to try to get selenium to scroll down and find more results
    """
    last_height = driver.execute_script('return document.body.scrollHeight')
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height
        time.sleep(sleep_time)


def resolve_pub_date(pub_date_obj):
    """ Helper function to attempt to resolve pub date from a BS object
    and convert the minimal pub date info into something Django will like. """
    pub_date = None
    if pub_date_obj:
        pub_date_str = pub_date_obj['datetime']
        pub_date = make_aware(datetime.fromisoformat(pub_date_str))
    return pub_date


def authed_li_jobs(user, url):
    """
    Authenticates via selenium and imports customized job feed.
    See https://medium.com/nerd-for-tech/linked-in-web-scraper-using-selenium-15189959b3ba
    better yet: https://medium.com/@alaeddine.grine/linkedin-job-scraper-and-matcher-85d0308ef9aa

    """
    driver = webdriver.Chrome()
    print("Logging into Linkedin")
    driver.get('https://www.linkedin.com/login')
    time.sleep(1)
    username_input = driver.find_element("id", "username")
    username_input.send_keys(user.linkedin_username)
    password_input = driver.find_element("id", "password")
    password_input.send_keys(user.linkedin_password)
    password_input.send_keys(Keys.ENTER)
    print("Now going to jobs page")
    # TO-DO: How can we verify selenium login before proceeding?
    # we'll do 3 pages, because that seems arbitrary enough
    jobs = {}
    for page in [url, url + '&start=50', url + '&start=75']:
        driver.get(page)
        scroll_to_bottom(driver)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        job_cards = soup.find_all('div', class_="job-card-container")
        print("# of cards found in selenium:", len(job_cards))
        
        for card in job_cards:
            job_id = card['data-job-id']

            title = card.find('a', class_='job-card-list__title')
            # LI puts a duplicate child in we don't want, so we'll get the first child
            title = title.find('span').text.strip()
            
            link = card.find('a', class_="job-card-container__link")
            if link:
                link = "https://linkedin.com" + link['href']

            # Salary may or may not be present, so we'll check first:
            salary = card.find('span', class_='artdeco-entity-lockup__metadata')
            if salary:
                salary = salary.text.strip()
            
            pub_date = resolve_pub_date(card.find('time', class_='job-search-card__listdate'))
            company = card.find('span', class_='job-card-container__primary-description').text.strip()

            if company not in BLOCK_LIST:
                jobs[job_id] = {
                    'title': title,
                    'link': link,
                    'company': company,
                    'location': card.find('div', class_='artdeco-entity-lockup__caption').text.strip(),
                    'salary': salary,
                    'pub_date': pub_date
                }
    driver.close()
    return jobs


def unauthed_li_jobs(url):
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print("Failed to get good requests response: ", r.status_code)
        return 
    soup = BeautifulSoup(r.content, "html.parser")
    job_cards = soup.find_all('div', class_="job-search-card")
    print("found jobs: ", len(job_cards))
    jobs = {}
    for card in job_cards:
        job_id = card['data-entity-urn'].rsplit(':')[-1]
        print(job_id)

        pub_date = resolve_pub_date(card.find('time', class_='job-search-card__listdate'))
        company = card.find('h4', class_='base-search-card__subtitle').text.strip()
        
        if company not in BLOCK_LIST:
            jobs[job_id] = {
                'title': card.find('h3', class_='base-search-card__title').text.strip(),
                'link': card.find('a', class_="base-card__full-link")['href'],
                'company': company,
                'location': card.find('span', class_='job-search-card__location').text.strip(),
                'pub_date': pub_date
            }
    return jobs
       
