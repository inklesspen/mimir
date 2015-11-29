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

  clearThreadPage() {
    this.dispatch();
  }
  updateThreadPage(threadPage) {
    this.dispatch(threadPage);
  }
}

module.exports = alt.createActions(ThreadActions);
