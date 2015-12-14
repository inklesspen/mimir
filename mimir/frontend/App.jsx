import React from 'react';
import ReactDOM from 'react-dom';
import {Router} from 'react-router';
import {routes} from './routes.jsx';
import {createHistory} from 'history';
import jsonrpc from './util/jsonrpc';
import Auth from './components/Auth.jsx';


function renderApp() {
    let history = createHistory();
    ReactDOM.render(
        <Router history={history}>{routes}</Router>,
        document.getElementById('ReactApp')
    );
}

function renderAuth() {
    ReactDOM.render(
        <Auth />,
        document.getElementById('ReactApp')
    );
}

function render(whoami) {
    if (whoami) {
        renderApp();
    } else {
        renderAuth();
    }
}

jsonrpc('whoami', []).then((whoami) => {
    navigator.id.watch({
        loggedInUser: whoami,
        onlogin: (assertion) => {
            jsonrpc('login', [assertion]).then((result) => {
                render(result.email);
            }).catch(() => {
                navigator.id.logout();
            });
        },
        onlogout: () => {
            jsonrpc('logout', []).then(() => {
                render();
            });
        }
    });
    render(whoami);
});
