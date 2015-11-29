import alt from '../altInstance';
import ThreadSource, {ThreadPageSource} from '../sources/ThreadSource';
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

export default alt.createStore(ThreadStore, 'ThreadStore');

class ThreadPageStore {
  constructor() {
    this.threadPage = null;
    this.exportAsync(ThreadPageSource);
    this.bindListeners({
        handleUpdate: ThreadActions.UPDATE_THREAD_PAGE,
        clear: ThreadActions.CLEAR_THREAD_PAGE
    });
  }

  clear() {
    this.threadPage = null;
  }

  handleUpdate(threadPage) {
    this.threadPage = threadPage;
  }
}

var TPS = alt.createStore(ThreadPageStore, 'ThreadPageStore');
// There's got to be a better way than this.
export {TPS as ThreadPageStore};
