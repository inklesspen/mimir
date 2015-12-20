import alt from '../altInstance';
import ThreadSource, {ThreadPageSource} from '../sources/ThreadSource';
import ThreadActions from '../actions/ThreadActions';

class ThreadStore {
  constructor() {
    this.threadInfo = {};
    this.exportAsync(ThreadSource);
    this.bindListeners({
      handleUpdateThreadInfo: ThreadActions.UPDATE_THREAD_INFO,
      threadInfoLoading: ThreadActions.FETCH_THREAD_INFO
    });
  }

  handleUpdateThreadInfo(threadInfo) {
    this.threadInfo = threadInfo;
  }

  threadInfoLoading() {
    this.threadInfo = {};
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
