import React from 'react';
import AltContainer from 'alt/AltContainer';
import WriteupOverview from './writeup_detail/WriteupOverview.jsx';
import {PostList} from './writeup_detail/Posts.jsx';
import {WriteupDetailStore} from '../stores/WriteupStore';
import WriteupActions from '../actions/WriteupActions';

export default class WriteupDetail extends React.Component {
    static willTransitionTo(transition, params, query, callback) {
        if (this.name === 'new-writeup') {
            // no writeup to load
            WriteupActions.clearWriteup();
            callback();
            return;
        }
        // maybe would be better to use transition.abort() and transition.retry()
        const id = parseInt(params.id, 10);
        if (isNaN(id)) {
            return callback(id);
        }
        var p = WriteupDetailStore.fetchWriteup(id);
        p.then(function() {
            callback();  // success
        }).catch(function(error) {
            callback(error.message);
        });
    }

    render() {
        return (
            <div className="container">
                <AltContainer store={WriteupDetailStore}>
                    <WriteupOverview />
                    <PostList />
                </AltContainer>
            </div>
        );
    }
}
