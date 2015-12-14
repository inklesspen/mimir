import React from 'react/addons';
import classNames from 'classnames';
import Immutable from 'immutable';
import WriteupActions from '../../actions/WriteupActions';
import {Link} from 'react-router';

class Post extends React.Component {
    render() {
        const originalLink = this.props.post.url ? (<small>(<a href={this.props.post.url}>Original</a>)</small>) : null;
        const title = this.props.post.title || '[Untitled]';
        const dest = `/admin/writeup/${this.props.writeupId}/post/${this.props.post.index}`;
        return (
            <tr>
                <td><Link to={dest}>{title}</Link> {originalLink}</td>
                <td>{this.props.post.author}</td>
                <td>{this.props.post.ordinal}</td>
            </tr>
        );
    }
}


export class PostList extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <table className="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Author</th>
                        <th>Ordinal</th>
                    </tr>
                </thead>
                <tbody>
                {this.props.detail.posts.map((post) => {
                    return (<Post key={post.index} writeupId={this.props.detail.id} post={post} />);
                 })}
                </tbody>
            </table>
        );
    }
}
