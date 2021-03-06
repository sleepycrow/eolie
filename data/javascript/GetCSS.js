var observer = new MutationObserver(subscriber);
var config = { childList: true, subtree: true };

function getLinks(head) {
    links = head.getElementsByTagName("link");
    for(let i=0; i<links.length; i++) {
        if (links[i].rel == "stylesheet") {
            alert("@EOLIE_CSS_URI@" + links[i].href);
        }
    }
}

function getStyles(head) {
    styles = head.getElementsByTagName("style");
    for(let i=0; i<styles.length; i++) {
        alert("@EOLIE_CSS_TEXT@" + styles[i].innerText)
    }
}

function subscriber(mutations) {
    html = document.querySelector("html");
    getLinks(html);
    getStyles(html);
}

html = document.querySelector("html");
getLinks(html);
getStyles(html);
observer.observe(html, config);
