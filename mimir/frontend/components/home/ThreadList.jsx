import React from 'react';
import {Link} from 'react-router';
import classNames from 'classnames';


class Thread extends React.Component {
    render() {
        var classes = classNames(
            "fa", "fa-lg",
            (this.props.thread.closed ? "fa-square-o" : "fa-check-square-o"),
        );
        const threadUrl = `http://forums.somethingawful.com/showthread.php?threadid=${this.props.thread.id}`;
        const lepLink = this.props.lastPost ? (<li><Link to={`/admin/threads/${this.props.thread.id}/page/${this.props.lastPost.page_num}`}>Last Extracted</Link></li>) : null;
        return (
            <tr>
                <td><Link to={`/admin/threads/${this.props.thread.id}/page/1`}>{this.props.thread.id}</Link></td>
                <td>{this.props.thread.page_count}</td>
                <td><span className={classes}></span></td>
                <td><ul className="list-inline">
                    <li>Mark Open/Closed (TODO)</li>
                    <li><a href={threadUrl}>Visit on SA</a></li>
                    {lepLink}
                </ul></td>
            </tr>
        );
    }
}


export default class ThreadList extends React.Component {
    render() {
        const threads = this.props.threadInfo.threads ? this.props.threadInfo.threads : [];
        const lep = this.props.threadInfo.last_extracted_post;
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
                {threads.map((thread) => {
                    return (<Thread key={thread.id} thread={thread} lastPost={thread.id === lep.thread_id ? lep : null} />);
                 })}
                </tbody>
            </table>
        );
    }
}
