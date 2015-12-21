import React from 'react';
import AltContainer from 'alt/AltContainer';
import WriteupOverview from './writeup_detail/WriteupOverview.jsx';
import {PostList} from './writeup_detail/Posts.jsx';
import {WriteupDetailStore} from '../stores/WriteupStore';
import WriteupActions from '../actions/WriteupActions';
import {Breadcrumbs, Breadcrumb} from './Breadcrumbs.jsx';
import appdata from '../appdata';

const applyRoot = appdata.get('applyRoot');

export default class WriteupDetail extends React.Component {
    static onEnter(nextState, replaceState, callback) {
        const params = nextState.params;
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
        const title = WriteupDetailStore.state.detail.title;
        return (
            <div className="container">
                <AltContainer store={WriteupDetailStore}>
                    <Breadcrumbs>
                        <Breadcrumb to={applyRoot('')} title="Home" />
                        <Breadcrumb active={true} title={`Writeup: ${title}`} />
                    </Breadcrumbs>
                    <hr />
                    <WriteupOverview />
                    <PostList />
                </AltContainer>
            </div>
        );
    }
}
