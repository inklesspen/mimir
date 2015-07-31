import alt from '../altInstance';
import WriteupSource from '../sources/WriteupSource';
import WriteupActions from '../actions/WriteupActions';

class WriteupStore {
  constructor() {
    this.writeups = [];
    this.exportAsync(WriteupSource);
    this.bindListeners({
        handleUpdate: WriteupActions.UPDATE_WRITEUPS
    });
  }

  handleUpdate(writeups) {
    this.writeups = writeups;
  }
}

export default alt.createStore(WriteupStore, 'WriteupStore');
