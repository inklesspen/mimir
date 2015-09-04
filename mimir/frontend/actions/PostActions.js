import alt from '../altInstance';
import jsonrpc from '../util/jsonrpc';

class PostActions {
  fetchFailed(message) {
    this.dispatch(message);
  }
  clearPost() {
    this.dispatch();
  }
  updatePost(post) {
    this.dispatch(post);
  }
  savePost(post) {
    jsonrpc('save_post', [post]).then(
      (savedPost) => {
        this.actions.updatePost(savedPost);
      }
    );
  }
}

export default alt.createActions(PostActions);
