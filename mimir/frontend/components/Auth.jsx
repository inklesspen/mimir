import React from 'react';
import jsonrpc from '../util/jsonrpc';

export default class Auth extends React.Component {
    loginHandler() {
        return (evt) => {
            evt.preventDefault();
            navigator.id.request();
        };
    }
    render() {
        return (
            <div className="container">
                <div className="col-md-12">
                <button type="button" onClick={this.loginHandler()} className="btn btn-success">Hoi</button>
                </div>
            </div>
        );
    }
}
