import React from 'react';
import routes from './routes.jsx';
import jsonrpc from './util/jsonrpc';
import Auth from './components/Auth.jsx';


function renderApp() {
    routes.run((Root) => {
        React.render(
            <Root />,
            document.getElementById('ReactApp')
        );
    });
}

function renderAuth() {
    React.render(
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
