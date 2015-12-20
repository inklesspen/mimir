import React from 'react';
import {Link} from 'react-router';

export class Breadcrumb extends React.Component {
    render () {
        if (this.props.active) {
            return (<li className="active">{this.props.title}</li>);
        }
        return (<li><Link to={this.props.to}>{this.props.title}</Link></li>);
    }
}

export class Breadcrumbs extends React.Component {
    render() {
        return (
            <ol className="breadcrumb">
                {this.props.children}
            </ol>
        );
    }
}
