import Immutable from 'immutable';

const bootstrapped = window.mimirData;


export default Immutable.Map([
  ["rootUrl", bootstrapped['root_url']],
  ["applyRoot", (url) => {
    url = (url ? url : '');
    url = (url[0] === "/" ? url.substr(1) : url);
    return bootstrapped['root_url'] + url;
  }],
  ["whoami", bootstrapped['whoami']]
]);
