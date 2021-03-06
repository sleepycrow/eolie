var loc = document.location;
var uri = {
  spec: loc.href,
  host: loc.host,
  prePath: loc.protocol + "//" + loc.host,
  scheme: loc.protocol.substr(0, loc.protocol.indexOf(":")),
  pathBase: loc.protocol + "//" + loc.host + loc.pathname.substr(0, loc.pathname.lastIndexOf("/") + 1)
};

if (typeof document !== 'undefined') {
    let documentClone = document.cloneNode(true);
    reader = new Readability(uri, documentClone);
    article = reader.parse();
    data = btoa(unescape(encodeURIComponent(article.content)));
    data;
}
