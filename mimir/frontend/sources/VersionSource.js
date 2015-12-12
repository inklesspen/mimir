import VersionActions from '../actions/VersionActions';
import jsonrpc from '../util/jsonrpc';

export var VersionSource = {
  fetchVersion: {
    remote(state, id) {
      return jsonrpc('get_wpv', [id]);
    },
    local(state, id) {
      return null;
    },
    success: VersionActions.updateVersion,
    error: VersionActions.fetchFailed,
    loading: VersionActions.clearVersion
  }
};
