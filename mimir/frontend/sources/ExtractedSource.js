import ExtractedActions from '../actions/ExtractedActions';
import jsonrpc from '../util/jsonrpc';

export var ExtractedSource = {
  fetchExtractedPosts() {
    return {
      remote() {
        return jsonrpc('extracted_list', []);
      },
      local() {
        return null;
      },
      // propagates threads to the store
      success: ExtractedActions.updateExtractedPosts,
      // propagates error message
      error: ExtractedActions.fetchFailed,
      // triggers store to prepare for the threads update
      loading: ExtractedActions.fetchExtractedPosts
    };
  }
};
