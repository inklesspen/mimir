import PostActions from '../actions/PostActions';
import jsonrpc from '../util/jsonrpc';

export var PostSource = {
  fetchPost: {
    remote(state, writeupId, postIndex) {
      return jsonrpc('post_detail', [writeupId, postIndex]);
    },
    local(state, writeupId, postIndex) {
      return null;
    },
    success: PostActions.updatePost,
    error: PostActions.fetchFailed,
    loading: PostActions.clearPost
  }
};
