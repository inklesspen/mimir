import ThreadActions from '../actions/ThreadActions';
import jsonrpc from '../util/jsonrpc';

export default {
  fetchThreadInfo() {
    return {
      remote() {
        return jsonrpc('thread_info', []);
      },
      local() {
        return null;
      },
      // propagates threads to the store
      success: ThreadActions.updateThreadInfo,
      // propagates error message
      error: ThreadActions.fetchFailed,
      // triggers store to prepare for the threads update
      loading: ThreadActions.fetchThreadInfo
    };
  }
};


export var ThreadPageSource = {
  fetchThreadPage: {
    remote(state, threadId, pageNum) {
      return jsonrpc('thread_page', [threadId, pageNum]);
    },
    local(state, threadId, pageNum) {
      return null;
    },
    success: ThreadActions.updateThreadPage,
    error: ThreadActions.fetchFailed,
    loading: ThreadActions.clearThreadPage
  }
};
