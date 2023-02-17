// THE FOLLOWING CODE WILL BE INJECTED IN THE BROWSER TO REQUEST FROM ETSY THE LISTINGS IDS

console.log('start::build_listing_ids_from_etsy2_1')
let node = document.querySelector('body > div:nth-child(1)')
let listing_ids = [];
let requests = [];
let pages = Number('@pages');

let pageButtons = Array.from(new Set(Array.from(document.querySelectorAll('a[href*="pagination&page="]')))).map(x => x.attributes.href.value)
if (pageButtons.length == 0) {
    if (node) {
        node.innerHTML = '<h1>DEBUG::AUTOMATION::No results found for keyword</h1>'
    }
    return [];
}

let pagesToRequest = Math.min(pages, pageButtons.length-2) //pageButtons.lengtht - 2 because the there 2 buttons that are "next" and "last" we dont want to take in consideration.


for (let i = 0; i < pagesToRequest; i++) {
    requests.push(fetch(`https://www.etsy.com/search?q=@keyword&explicit=1&is_best_seller=true&ship_to=US&page=` + i + 1, {
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Microsoft Edge\";v=\"109\", \"Chromium\";v=\"109\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        },
        "referrerPolicy": "strict-origin-when-cross-origin",
        "body": null,
        "method": "GET"
    }));
}
let responses = await Promise.all(requests);
let html_lists = await Promise.all(responses.map(r => r.text()));
for (let i = 0; i < html_lists.length; i++) {
    try {

        let listingFromAttr = Array.from(document.querySelectorAll('a[data-listing-id]')).map(x => x.dataset.listingId);
        if (listingFromAttr && listingFromAttr.length > 0) {
            listing_ids = listing_ids.concat(listingFromAttr.slice(0, Number('@listings_per_page')));
        }

        let lazyIndex = html_lists[i].indexOf("lazy_loaded_listing_ids")
        if (lazyIndex > 0) {
            let subpart = html_lists[i].substring(lazyIndex);
            let rows = subpart.substring(subpart.indexOf("["), subpart.indexOf("]") + 1)
            if (rows && rows.length > 0) {
                listing_ids = listing_ids.concat(JSON.parse(rows).slice(0, Number('@listings_per_page')));
            }
        }
    } catch (e) {
        console.log('error::build_listing_ids_from_etsy2_1::page' + (i+1));
        console.log(e);
    }
}

listing_ids = [...new Set(listing_ids.map(x => Number(x)).filter(x => !isNaN(x)))];

console.log('end::build_listing_ids_from_etsy2_1')
return listing_ids;