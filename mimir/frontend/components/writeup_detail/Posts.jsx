import React from 'react/addons';
import classNames from 'classnames';
import Immutable from 'immutable';
import WriteupActions from '../../actions/WriteupActions';
import {Link} from 'react-router';

class Post extends React.Component {
    render() {
        const originalLink = this.props.post.url ? (<small>(<a href={this.props.post.url}>Original</a>)</small>) : null;
        return (
            <tr>
                <td><Link to="post-detail" params={{writeupId: this.props.writeupId, postIndex: this.props.post.index}}>{this.props.post.title}</Link> {originalLink}</td>
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
                    <tr>
                        <td>
                            <Link to="new-post" params={{writeupId: this.props.detail.id}}>Add <span className="fa fa-lg fa-plus" aria-hidden="true"></span></Link>
                        </td>
                        <td />
                        <td />
                    </tr>
                </tbody>
            </table>
        );
    }
}