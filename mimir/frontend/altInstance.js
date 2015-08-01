import Alt from 'alt';
var alt = new Alt();

if (window.connectIframeAltDevtools) {
  parent['alt.js.org'] = alt;
} else {
  window['alt.js.org'] = alt;
}

module.exports = alt;
