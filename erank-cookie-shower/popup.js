const go = document.getElementById("go");
const input = document.getElementById("input");
const message = document.getElementById("message");

var port = null;
// The async IIFE is necessary because Chrome <89 does not support top level await.
(async function initPopupWindow() {



})();



// chrome.runtime.onMessage.addListener(
//   function (request, sender, sendResponse) {
//     console.log(sender.tab ?
//       "from a content script:" + sender.tab.url :
//       "from the extension");
//   }
// );


