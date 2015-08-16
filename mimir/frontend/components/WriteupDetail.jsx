import React from 'react';
import AltContainer from 'alt/AltContainer';
import WriteupOverview from './writeup_detail/WriteupOverview.jsx';
import {WriteupDetailStore} from '../stores/WriteupStore';

export default class WriteupDetail extends React.Component {
    static willTransitionTo(transition, params, query, callback) {
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
                </AltContainer>
            </div>
        );
    }
}
