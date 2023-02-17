import traceback
import pandas as pd
import json
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from typing import List
from datetime import datetime
#from .scrape_erank import get_erank_data_bulk
#rom .models import create_scrape_data, buildLogger
import scrape_erank
import models as models
import utils
import openpyxl
import os
import asyncio
import urllib.parse


log = utils.buildLogger('scrape_etsy')

def save_to_json(data: dict, filename: str):
    with open(filename, 'w') as f:
        json.dump(data, f)


def read_from_json(filename: str) -> List[dict]:
    with open(filename, 'r') as f:
        rs = json.load(f)
        return rs

def get_listings_ids(browser: Chrome, listin_per_page: int) -> list:
    listings_ids = []
    region:WebElement = WebDriverWait(browser, 7).until(lambda x: x.find_element(
        by=By.CSS_SELECTOR, value='div[data-search-results-region]'))
    if region is None:
        log.warn('region::not_found::div[data-search-results-region]')
        return []
    log.debug('region::found::div[data-search-results-region]')

    listings = region.find_elements(
        by=By.CSS_SELECTOR, value='a[data-listing-id]')

    for list in listings:
        attr = list.get_dom_attribute('data-listing-id')
        listings_ids.append(attr)
    log.debug('listings count: {}'.format(len(listings_ids)))
    if listin_per_page >= 1:
        return listings_ids[0:listin_per_page]
    else:
        return listings_ids


def get_page_dom(browser: Chrome, next_page: int) -> WebElement:
    page_doms: List[WebElement] = WebDriverWait(browser, 10).until(lambda x: x.find_elements(
        by=By.CSS_SELECTOR, value='.wt-action-group__item-container > a[href*="page={}"]'.format(next_page)))
    log.debug('len page_doms: {}'.format(len(page_doms)))
    if page_doms is None or len(page_doms) == 0:
        return None
    return page_doms[1]


def create_xlsx_file(file_name:str):
    #now = datetime.now().strftime("%d%m%Y_%H_%M_%S")
    file_name = 'static/{}'.format(file_name)
    # Create a new workbook object
    workbook = openpyxl.Workbook()
    # Save the workbook to an XLSX file
    workbook.save('{}'.format(file_name))

# this slower version of extracting data from etsy
def build_listing_ids_from_etsy(pages_per_keyword, listings_per_page, browser) -> list:
    listings_ids = []
    listings_ids.extend(get_listings_ids(browser, listings_per_page))

    for i in range(1, pages_per_keyword):
        log.debug('moving to next page :: i:: {}'.format(i+1))
        page_button: WebElement = get_page_dom(browser, i+1)
        if page_button is None:
            log.debug('page not found :: i+1 {}'.format(i+1))
            break
        log.debug('page_button_text:: {}'.format(page_button.text))
        ActionChains(browser).move_to_element(page_button).click(page_button).perform()
        WebDriverWait(browser, 10).until(lambda x: x.find_element(by=By.CSS_SELECTOR, value='div.wt-display-none[data-listing-card-skeleton-grid]'))
        listings_ids.extend(get_listings_ids(browser, listings_per_page))
        log.debug('listings_ids: '.format(listings_ids))
    return listings_ids


etsy_file_content = None

def read_etsyjs() -> str:
    global etsy_file_content
    if etsy_file_content is not None:
        return etsy_file_content
    file_name = 'static/scripts/{}'.format('etsy.js')
    # read file
    with open(file_name, 'r') as myfile:
        etsy_file_content = myfile.read()
        print(etsy_file_content)
        return etsy_file_content

# this is a faster version of extracting data from etsy
def build_listing_ids_from_etsy_2(pages_per_keyword:int, keyword:str, listings_per_page:int, browser:Chrome) -> list:
    jscode = read_etsyjs() \
    .replace("@pages", str(pages_per_keyword)) \
    .replace("@keyword", urllib.parse.quote(keyword)) \
    .replace("@listings_per_page", str(listings_per_page))
    listing_ids = browser.execute_script(jscode)
    return listing_ids



CONFIG_SCRAPE_FROM_ERANK = True

async def run_etsay_erank_data(keywords: list[str], cookie_erank:str, pages_per_keyword: int,  listings_per_page:int, file_name:str) -> bool:
    """
    total_pages:  is basically pages per keyword
    total_listings: is basically listing per page keyword
    """
    state = True
    browser = Chrome(executable_path=os.path.join('/chromedriver_win32/','chromedriver.exe'))
    try:
        assert keywords is not None and len(keywords) > 0 , 'no keywords'
        assert cookie_erank is not None , 'cookie_erank is required'
        assert file_name is not None , 'file_name is required'
        assert pages_per_keyword > 0 and pages_per_keyword <= 8, 'total_pages must be greater than 0 and less than 8.'
        assert listings_per_page > 0 and listings_per_page <= 64, 'total_listings must be greater than 0 and less than 24.'

        print("keywords {} ".format(keywords))

        create_xlsx_file(file_name)

        log.debug('total keywords :{} '.format(len(keywords)))
        log.debug('pages per keyword : {}'.format(pages_per_keyword))
        log.debug('listing per page : {}'.format( listings_per_page))

        for index, keyword in enumerate(keywords):
            log.debug('moving to next keyword :: {}'.format(keyword))

            browser.get('https://www.etsy.com/search?q={}&explicit=1&is_best_seller=true&ship_to=US'.format(urllib.parse.quote(keyword)))

            listings_ids = []

            #listings_ids = build_listing_ids_from_etsy(pages_per_keyword, listings_per_page, browser)
            listings_ids = build_listing_ids_from_etsy_2(pages_per_keyword,keyword, listings_per_page, browser)

            if listings_ids is None or len(listings_ids) == 0:
                log.debug('no listings_ids found for keyword :: {}'.format(keyword))
                continue

            if CONFIG_SCRAPE_FROM_ERANK is False:
                log.debug("{}".format(listings_ids))
                continue

            erank_data_list = await scrape_erank.get_erank_data_bulk(keyword, cookie_erank, listings_ids)
            ## log.debug('calling saving to json file')
            ## save_to_json(erank_data_list, 'erank_data_list_{}.json'.format(now))
            if erank_data_list is not None and len(erank_data_list) > 0:
                log.debug('appending to excel file total rows {}'.format(len(erank_data_list)))
                df = pd.DataFrame.from_records(erank_data_list)
                with pd.ExcelWriter('static/'+file_name, mode='a') as writer:
                    sheet_name_var = '{}'.format(keyword[:30])  # limit of 30 charecters name
                    df.to_excel(writer, sheet_name=sheet_name_var, index=False)
            else:
                log.warning('NO DATA:: no data to append to excel file')
        log.debug('done')
    except Exception as e:
        state = False
        log.warning("ERRROR!!!!!")
        log.warning(str(e))
        log.warning(traceback.format_exc())

    finally:
        browser.quit()
    return state


# if __name__ == '__main__':
#     cookie = ""
#     asyncio.run(run_etsay_erank_data(keywords=['Funny Sweatshirt', 'Rtx 3060'], cookie_erank= cookie, pages_per_keyword=8,  listings_per_page=4, file_name="test.xlsx"))
#     print('done')