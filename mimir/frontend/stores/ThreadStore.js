import alt from '../altInstance';
import ThreadSource from '../sources/ThreadSource';
import ThreadActions from '../actions/ThreadActions';

class ThreadStore {
  constructor() {
    this.threads = [];
    this.exportAsync(ThreadSource);
    this.bindListeners({
      handleUpdateThreads: ThreadActions.UPDATE_THREADS,
      threadsLoading: ThreadActions.FETCH_THREADS
    });
  }

  handleUpdateThreads(threads) {
    this.threads = threads;
  }

  threadsLoading() {
    this.threads = [];
  }
}

module.exports = alt.createStore(ThreadStore, 'ThreadStore');
