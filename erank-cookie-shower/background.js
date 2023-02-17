
let erankHeaders = [];

chrome.runtime.onInstalled.addListener(() => {
  console.log('installed');
});
chrome.webRequest.onBeforeSendHeaders.addListener(
  function (details) {
    if (details.url.startsWith('https://erank.com/listing-audit/'))
    {
      console.log(details)
      erankHeaders = details.requestHeaders;
    }
  },
  {
    urls: ["https://erank.com/listing-audit/*"],
    // types: ["main_frame"]
  },
  ["extraHeaders", "requestHeaders"]
);


chrome.runtime.onConnect.addListener(function (port) {
  console.log('port.name :: ', port.name);
  console.assert(port.name === "erank_cookie_shower");
  port.onMessage.addListener(function (msg) {
    if (msg.request == 'cookie') {
      port.postMessage({ response: erankHeaders.length == 0 ? 'cookie_poll' : erankHeaders });
    }
  });
});

