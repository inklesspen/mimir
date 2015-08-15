import React from 'react';
import AltContainer from 'alt/AltContainer';
import WriteupOverview from './writeup_detail/WriteupOverview.jsx';
import {WriteupDetailStore} from '../stores/WriteupStore';

export default class WriteupDetail extends React.Component {
    static willTransitionTo(transition, params, query, callback) {
        // maybe would be better to use transition.abort() and transition.retry()
        var p = WriteupDetailStore.fetchWriteup(params.id);
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
                </AltContainer>
            </div>
        );
    }
}
