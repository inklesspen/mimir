import alt from '../altInstance';
import jsonrpc from '../util/jsonrpc';

class VersionActions {
  clearVersions() {
    this.dispatch();
  }
  updateVersions(versions) {
    this.dispatch(versions);
  }
  fetchFailed(message) {
    this.dispatch(message);
  }
  clearVersion() {
    this.dispatch();
  }
  updateVersion(version) {
    this.dispatch(version);
  }
  saveVersion(version) {
    jsonrpc('save_wpv', [version]).then(
      (savedVersion) => {
        this.actions.updateVersion(savedVersion);
      }
    );
  }
}

export default alt.createActions(VersionActions);
