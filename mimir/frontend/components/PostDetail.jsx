import React from 'react';
import AltContainer from 'alt/AltContainer';
import {PostStore} from '../stores/PostStore';
import PostActions from '../actions/PostActions';
import {PostOverview} from './post_detail/PostOverview.jsx';
import {VersionList} from './post_detail/VersionList.jsx';

export default class PostDetail extends React.Component {
    static onEnter(nextState, replaceState, callback) {
        const params = nextState.params;
        const writeupId = parseInt(params.writeupId, 10);
        if (isNaN(writeupId)) {
            return callback(writeupId);
        }
        const postIndex = parseInt(params.postIndex, 10);
        if (isNaN(postIndex)) {
            return callback(postIndex);
        }
        var p = PostStore.fetchPost(writeupId, postIndex);
        p.then(function() {
            callback();  // success
        }).catch(function(error) {
            callback(error.message);
        });
    }

    render() {
        return (
            <div className="container">
                <AltContainer store={PostStore}>
                    <PostOverview routeParams={this.props.params} />
                    <VersionList routeParams={this.props.params} />
                </AltContainer>
            </div>
        );
    }
}
