import React from 'react';
import {Link} from 'react-router';
import classNames from 'classnames';


class BoolCheckSpan extends React.Component {
    render() {
        var classes = classNames(
            "fa", "fa-lg",
            (this.props.value ? "fa-check-square-o" : "fa-square-o"),
        );
        return (<span className={classes}></span>);
    }
}


class Writeup extends React.Component {
    render() {
        return (
            <tr>
                <td><Link to="writeup-detail" params={{id: this.props.writeup.id}}>{this.props.writeup.title}</Link></td>
                <td>{this.props.writeup.author_slug}</td>
                <td>{this.props.writeup.status}</td>
                <td><BoolCheckSpan value={this.props.writeup.published} /></td>
            </tr>
        );
    }
}


export default class WriteupList extends React.Component {
    render() {
        return (
            <table className="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Writeup</th>
                        <th>Author</th>
                        <th>Status</th>
                        <th>Published</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><Link to="new-writeup">Add <span className="fa fa-lg fa-plus" aria-hidden="true"></span></Link></td>
                        <td />
                        <td />
                        <td />
                    </tr>
                {this.props.writeups.map((writeup) => {
                    return (<Writeup key={writeup.id} writeup={writeup} />);
                 })}
                </tbody>
            </table>
        );
    }
}
