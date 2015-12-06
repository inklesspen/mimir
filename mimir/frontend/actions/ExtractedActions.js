import alt from '../altInstance';

class ExtractedActions {
  fetchExtractedPosts() {
    this.dispatch();
  }
  updateExtractedPosts(extractedPosts) {
    this.dispatch(extractedPosts);
  }
  fetchFailed(message) {
    this.dispatch(message);
  }
}

module.exports = alt.createActions(ExtractedActions);
