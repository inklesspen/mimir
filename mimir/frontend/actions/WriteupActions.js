import alt from '../altInstance';

class WriteupActions {
  fetchWriteups() {
    this.dispatch();
  }
  updateWriteups(writeups) {
    this.dispatch(writeups);
  }
  fetchFailed(message) {
    this.dispatch(message);
  }
}

export default alt.createActions(WriteupActions);
