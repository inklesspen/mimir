import React from 'react';
import AltContainer from 'alt/AltContainer';
import {PostStore} from '../stores/PostStore';
import PostActions from '../actions/PostActions';
import {PostOverview} from './post_detail/PostOverview.jsx';
import {VersionList} from './post_detail/VersionList.jsx';
import {Breadcrumbs, Breadcrumb} from './Breadcrumbs.jsx';
import appdata from '../appdata';

const applyRoot = appdata.get('applyRoot');

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
        const writeupTitle = PostStore.state.post.writeup_title;
        const writeupId = PostStore.state.post.writeup_id;
        const title = PostStore.state.post.title;
        return (
            <div className="container">
                <AltContainer store={PostStore}>
                    <Breadcrumbs>
                        <Breadcrumb to={applyRoot('')} title="Home" />
                        <Breadcrumb to={applyRoot(`writeup/${writeupId}`)} title={`Writeup: ${writeupTitle}`} />
                        <Breadcrumb active={true} title={`Post: ${title}`} />
                    </Breadcrumbs>
                    <hr />
                    <PostOverview routeParams={this.props.params} />
                    <VersionList routeParams={this.props.params} />
                </AltContainer>
            </div>
        );
    }
}
