import alt from '../altInstance';

class ThreadActions {
  fetchThreads() {
    this.dispatch();
  }
  updateThreads(threads) {
    this.dispatch(threads);
  }
  fetchFailed(message) {
    this.dispatch(message);
  }
}

module.exports = alt.createActions(ThreadActions);
