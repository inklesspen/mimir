import React from 'react';
import classNames from 'classnames';
import {Link} from 'react-router';
import jsonrpc from '../../util/jsonrpc';
import {PostStore} from '../../stores/PostStore';

class Version extends React.Component {
    activateHandler() {
        return (evt) => {
            evt.preventDefault();
            jsonrpc('activate_version', [this.props.version.id]).then(() => {
                const writeupId = parseInt(this.props.routeParams.writeupId, 10);
                const postIndex = parseInt(this.props.routeParams.postIndex, 10);
                return PostStore.fetchPost(writeupId, postIndex);
            });
        };
    }

    render() {
        var classes = classNames(
            "fa", "fa-lg",
            (this.props.version.active ? "fa-check-square-o" : "fa-square-o"),
        );
        var actions = [];
        actions.push((<li key="1"><a role="button" href="#" onClick={this.props.onSelect}>View</a></li>));
        if (!this.props.version.active) {
            actions.push((<li key="2"><a role="button" href="#" onClick={this.activateHandler()}>Activate</a></li>));
        }
        const dest = `/admin/editor/${this.props.version.id}`;
        actions.push((<li key="3">
            <Link to={dest}>Copy and Edit</Link>
        </li>));
        return (
            <tr>
                <td>{this.props.version.version}</td>
                <td>{this.props.version.edit_summary}</td>
                <td><span className={classes}></span></td>
                <td><ul className="list-inline">{actions}</ul></td>
            </tr>
        );
    }
}

export class VersionList extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedIndex: null
        };
    }
    clickHandler(index) {
        return (evt) => {
            evt.preventDefault();
            this.setState({selectedIndex: index});
        };
    }

    getHtmlView() {
        if (this.state.selectedIndex !== null) {
            return {
                __html: this.props.post.versions[this.state.selectedIndex].html
            };
        }
    }

    render() {
        if (!this.props.post) {
            return null;
        }
        return (
            <div>
                <table className="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Version</th>
                            <th>Summary</th>
                            <th>Active</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                    {this.props.post.versions.map((version, index) => (
                        <Version key={version.version} version={version} onSelect={this.clickHandler(index)} routeParams={this.props.routeParams}/>
                     ))}
                    </tbody>
                </table>
                <hr />
                <div dangerouslySetInnerHTML={this.getHtmlView()}></div>
            </div>
        );
    }
}
