import alt from '../altInstance';
import jsonrpc from '../util/jsonrpc';

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
  saveWriteup(writeup) {
    jsonrpc('save_writeup', [writeup]).then(
      (savedWriteup) => {
        this.actions.updateWriteup(savedWriteup);
      }
    );
  }
}

export default alt.createActions(WriteupActions);
