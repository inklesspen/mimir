import alt from '../altInstance';
import {PostSource} from '../sources/PostSource';
import PostActions from '../actions/PostActions';

class PostStore {
  constructor() {
    this.post = null;
    this.exportAsync(PostSource);
    this.bindListeners({
        handleUpdate: PostActions.UPDATE_POST,
        clear: PostActions.CLEAR_POST
    });
  }

  clear() {
    this.post = null;
  }

  handleUpdate(post) {
    this.post = post;
  }
}

var PS = alt.createStore(PostStore, 'PostStore');
// There's got to be a better way than this.
export {PS as PostStore};
