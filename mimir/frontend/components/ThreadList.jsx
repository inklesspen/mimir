import React from 'react';
import classNames from 'classnames';


class Thread extends React.Component {
    render() {
        var classes = classNames(
            "fa", "fa-lg",
            (this.props.thread.closed ? "fa-square-o" : "fa-check-square-o"),
        );
        var threadUrl = `http://forums.somethingawful.com/showthread.php?threadid=${this.props.thread.id}`;
        return (
            <tr>
                <td><a href={threadUrl}>{this.props.thread.id}</a></td>
                <td>{this.props.thread.page_count}</td>
                <td><span className={classes}></span></td>
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
