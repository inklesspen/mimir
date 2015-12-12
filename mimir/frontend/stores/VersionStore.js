import alt from '../altInstance';
import {VersionSource} from '../sources/VersionSource';
import VersionActions from '../actions/VersionActions';

class VersionStore {
  constructor() {
    this.version = null;
    this.exportAsync(VersionSource);
    this.bindListeners({
        handleUpdate: VersionActions.UPDATE_VERSION,
        clear: VersionActions.CLEAR_VERSION
    });
  }

  clear() {
    this.version = null;
  }

  handleUpdate(version) {
    this.version = version;
  }
}

var VS = alt.createStore(VersionStore, 'VersionStore');
// There's got to be a better way than this.
export {VS as VersionStore};
