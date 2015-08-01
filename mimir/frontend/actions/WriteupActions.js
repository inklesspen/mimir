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
  fetchWriteup() {
    this.dispatch();
  }
  updateWriteup(writeup) {
    this.dispatch(writeup);
  }
}

export default alt.createActions(WriteupActions);
