import alt from '../altInstance';
import WriteupSource, {WriteupDetailSource} from '../sources/WriteupSource';
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

class WriteupDetailStore {
  constructor() {
    this.detail = null;
    this.exportAsync(WriteupDetailSource);
    this.bindListeners({
        handleUpdate: WriteupActions.UPDATE_WRITEUP,
        clear: WriteupActions.CLEAR_WRITEUP
    });
  }

  clear() {
    this.detail = null;
  }

  handleUpdate(detail) {
    this.detail = detail;
  }
}

var WDS = alt.createStore(WriteupDetailStore, 'WriteupDetailStore');
// There's got to be a better way than this.
export {WDS as WriteupDetailStore};
