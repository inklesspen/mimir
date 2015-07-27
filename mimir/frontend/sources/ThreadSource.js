import ThreadActions from '../actions/ThreadActions';
require('whatwg-fetch'); // fetch pollutes the global namespace

var mockData = [
  {'id': 123, 'page_count': 1000, 'closed': true},
  {'id': 456, 'page_count': 2000, 'closed': false}
];

export default {
  fetchThreads() {
    return {
      remote() {
        return new Promise(function(resolve, reject) {
          setTimeout(function() {
            resolve(mockData);
          }, 25);
        });
      },
      local() {
        return null;
      },
      // propagates threads to the store
      success: ThreadActions.updateThreads,
      // propagates error message
      error: ThreadActions.fetchFailed,
      // triggers store to prepare for the threads update
      loading: ThreadActions.fetchThreads
    };
  }
};
