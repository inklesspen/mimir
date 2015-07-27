require('whatwg-fetch'); // fetch pollutes the global namespace

const apiUrl = '/api';

let idCounter = 1;

function checkStatus(response) {
  if (response.status >= 200 && response.status < 300) {
    return response;
  } else {
    // maybe add more details? i dunno
    return Promise.reject(response.statusText);
  }
}

function parseJSON(response) {
  return response.json();
}

export default function jsonrpc(method, params) {
  const postBody = {
    jsonrpc: "2.0",
    method: method,
    params: params,
    id: idCounter++
  };
  return fetch(apiUrl, {
    method: 'post',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(postBody)
  }).then(checkStatus).then(parseJSON).then(function(response) {
    if (response.jsonrpc !== postBody.jsonrpc) {
      return Promise.reject("invalid jsonrpc version");
    }
    if (response.id !== postBody.id) {
      return Promise.reject("invalid jsonrpc id");
    }
    if (!response.hasOwnProperty('error') && !response.hasOwnProperty('result')) {
      return Promise.reject('malformed response');
    }
    if (response.hasOwnProperty('error')) {
      return Promise.reject(response.error);
    }
    return response.result;
  });
}
