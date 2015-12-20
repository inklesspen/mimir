import alt from '../altInstance';

class ThreadActions {
  fetchThreadInfo() {
    this.dispatch();
  }
  updateThreadInfo(threadInfo) {
    this.dispatch(threadInfo);
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
