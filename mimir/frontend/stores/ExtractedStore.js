import alt from '../altInstance';
import {ExtractedSource} from '../sources/ExtractedSource';
import ExtractedActions from '../actions/ExtractedActions';

class ExtractedStore {
  constructor() {
    this.extractedPosts = [];
    this.exportAsync(ExtractedSource);
    this.bindListeners({
      handleUpdateExtractedPosts: ExtractedActions.UPDATE_EXTRACTED_POSTS,
      extractedPostsLoading: ExtractedActions.FETCH_EXTRACTED_POSTS
    });
  }

  handleUpdateExtractedPosts(extractedPosts) {
    this.extractedPosts = extractedPosts;
  }

  extractedPostsLoading() {
    this.extractedPosts = [];
  }
}

export default alt.createStore(ExtractedStore, 'ExtractedStore');
