import ThreadActions from '../actions/ThreadActions';
import jsonrpc from '../util/jsonrpc';

export default {
  fetchThreads() {
    return {
      remote() {
        return jsonrpc('thread_info', []);
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
