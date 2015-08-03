import React from 'react';
import AltContainer from 'alt/AltContainer';
import ThreadList from './home/ThreadList.jsx';
import WriteupList from './home/WriteupList.jsx';
import ThreadStore from '../stores/ThreadStore';
import WriteupStore from '../stores/WriteupStore';

export default class Home extends React.Component {
    componentDidMount() {
        ThreadStore.fetchThreads();
        WriteupStore.fetchWriteups();
    }
    render() {
        return (
            <div className="container">
                <div className="col-md-3">
                    <div className="bs-sidebar hidden-print affix well" role="complementary">
                        <ul className="nav bs-sidenav">
                            <li>Audit log stuff goes here</li>
                        </ul>
                    </div>
                </div>
                <div className="col-md-9" role="main">
                    <AltContainer store={ThreadStore}>
                        <ThreadList />
                    </AltContainer>
                    <hr />
                    <AltContainer store={WriteupStore}>
                        <WriteupList />
                    </AltContainer>
                </div>
            </div>
        );
    }
}
