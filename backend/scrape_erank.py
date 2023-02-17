import asyncio
from typing import List
import aiohttp
import ssl
from bs4 import BeautifulSoup
import utils

log = utils.buildLogger('scrape_erank')

class CustomResponseObject:
    def __init__(self, url: str, status_code: int, response_url: str = ''):
        self.url: str = url
        self.status_code = status_code
        self.text: str = ''
        self.res_url:str = response_url

async def fetch(session: aiohttp.ClientSession, url: str):
    async with session.get(url, ssl=ssl.SSLContext()) as response:
        res = CustomResponseObject(url, response.status, str(response.url))
        try:
            res.text = await response.text(encoding='utf-8')
            return res
        except Exception as e:
            log.error('Exception for URl:::{} in fetch :: {}'.format(url,e))
            res.text = ''
            return res


async def fetch_all(urls, headers_dict) -> List[CustomResponseObject]:
    """Crawl & write concurrently to `file` for multiple `urls`."""
    async with aiohttp.ClientSession(headers=headers_dict) as session:
        tasks = []
        for url in urls:
            tasks.append(fetch( session=session, url=url))
        results = await asyncio.gather(*tasks)
        return results


def split_url_by(url_list, x):
    count = 1
    req_by_x = []
    for i, url in enumerate(url_list):
        req_by_x.append(url)
        if count % x == 0:
            yield req_by_x
            req_by_x = []
            count = 1
        else:
            count += 1

    if len(req_by_x) > 0:
        yield req_by_x


async def get_erank_data_bulk(keyword: str, cookie_erank: str, listingids) -> List[dict]:
    assert len(listingids) > 0
    assert keyword != ''
    assert cookie_erank != ''
    # write a breakpoint here to debug the code
    log.debug('calling erank api')

    urls = ["https://erank.com/listing-audit/{}".format(listingid) for listingid in listingids]

    headers_dict = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "cookie": cookie_erank
    }

    return_data_list = []
    for urls in split_url_by(urls, 2):
        res_objects: List[CustomResponseObject] = await fetch_all(urls, headers_dict)
        for res in res_objects:
            log.debug('erank res {} {} {}' .format(res.url, res.status_code,  res.res_url))
            listing_id = res.url.split('/')[-1]
            listing_url = 'https://www.etsy.com/listing/{}'.format(listing_id)
            data = utils.create_scrape_data(listing_url=listing_url, listing_id=listing_id,
                                   keyword=keyword, http_status_code=res.status_code)
            soup: BeautifulSoup = BeautifulSoup(res.text, 'html.parser')
            stats = soup.select('#listing-statistics-div  p.amount')
            if stats is not None and len(stats) > 1:
                data['VISIBILITY_SCORE'] = stats[0].text.strip()
                data['DAILY_VIEWS'] = stats[2].text.strip()
                data['LISTING_AGE'] = stats[3].text.strip()
                log.debug('erank_data: {}'.format(data))
            else:
                data['ERROR'] = 'CONTENT NOT FOUND (check manually)'
                log.warning('nop stats found at etsy.com, for listing_id: {}'.format(listing_id))
            return_data_list.append(data)
    return return_data_list


# if __name__ == '__main__':
#     cookie = ""
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     content = asyncio.run(get_erank_data_bulk('test', cookie , ['1332602271']))
#     print(content)
#     print('done')