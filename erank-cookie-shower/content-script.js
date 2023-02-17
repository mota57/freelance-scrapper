(async function initPopupWindow() {

  try {
    port = chrome.runtime.connect({ name: "erank_cookie_shower" });

    port.postMessage({ request: "cookie" });
    console.log('connected');

    port.onMessage.addListener(function (msg) {

      console.log('debug::msg:: ', msg)

      if (msg.response == 'cookie_poll')
      {
        setTimeout(function () {
          port.postMessage({ request: "cookie" });
        }, 1000);
      } else if (msg.response && msg.response.length > 0 && msg.response.findIndex(x => x.name == 'Cookie') >= 0)
      {
        let cookie =  msg.response.find(x => x.name == 'Cookie');
        prompt('copy text selected', cookie.value);
        // chrome.runtime.sendMessage({ cookie: msg.response }).then(function (res) {});
      } else {
        alert('no cookie are you sure you are at the right url???');
      }

    });
  } catch (e) {
    console.error(e);
  }

})();
