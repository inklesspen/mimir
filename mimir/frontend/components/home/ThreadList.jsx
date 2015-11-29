import React from 'react';
import {Link} from 'react-router';
import classNames from 'classnames';


class Thread extends React.Component {
    render() {
        var classes = classNames(
            "fa", "fa-lg",
            (this.props.thread.closed ? "fa-square-o" : "fa-check-square-o"),
        );
        var threadUrl = `http://forums.somethingawful.com/showthread.php?threadid=${this.props.thread.id}`;
        // TODO: make the thread id link to a thread-browsing page
        return (
            <tr>
                <td><Link to="thread-page" params={{id: this.props.thread.id, page: 1}}>{this.props.thread.id}</Link></td>
                <td>{this.props.thread.page_count}</td>
                <td><span className={classes}></span></td>
                <td><ul className="list-inline">
                    <li>Mark Open/Closed (TODO)</li>
                    <li><a href={threadUrl}>Visit on SA</a></li>
                </ul></td>
            </tr>
        );
    }
}


export default class ThreadList extends React.Component {
    render() {
        return (
            <table className="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Thread</th>
                        <th>Page Count</th>
                        <th>Open/Active</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                {this.props.threads.map((thread) => {
                    return (<Thread key={thread.id} thread={thread} />);
                 })}
                </tbody>
            </table>
        );
    }
}
