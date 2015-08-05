import WriteupActions from '../actions/WriteupActions';
import jsonrpc from '../util/jsonrpc';

export default {
  fetchWriteups() {
    return {
      remote() {
        return jsonrpc('writeup_list', []);
      },
      local() {
        return null;
      },
      // propagates threads to the store
      success: WriteupActions.updateWriteups,
      // propagates error message
      error: WriteupActions.fetchFailed,
      // triggers store to prepare for the threads update
      loading: WriteupActions.fetchWriteups
    };
  }
};

export var WriteupDetailSource = {
  fetchWriteup: {
    remote(state, id) {
      return jsonrpc('writeup_detail', [id]);
    },
    local(state, id) {
      return null;
    },
    success: WriteupActions.updateWriteup,
    error: WriteupActions.fetchFailed,
    loading: WriteupActions.fetchWriteup
  }
};
