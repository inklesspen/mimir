import React from 'react';
import AltContainer from 'alt/AltContainer';
import Locations from './Locations.jsx';
import ThreadList from './ThreadList.jsx';
import ThreadStore from '../stores/ThreadStore';

export default class Admin extends React.Component {
    componentDidMount() {
        ThreadStore.fetchThreads();
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
                    {/* <Locations /> */}
                </div>
            </div>
        );
    }
}
