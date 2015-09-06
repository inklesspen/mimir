import React from 'react';
import classNames from 'classnames';

class Version extends React.Component {
    render() {
        var classes = classNames(
            "fa", "fa-lg",
            (this.props.version.active ? "fa-check-square-o" : "fa-square-o"),
        );
        return (
            <tr>
                <td><a role="button" href="#" onClick={this.props.onSelect}>{this.props.version.version}</a></td>
                <td>N/A yet</td>
                <td><span className={classes}></span></td>
                <td>TBD</td>
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
        return () => {
            console.log(index);
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
                    {this.props.post.versions.map((version, index) => {
                        return (<Version key={version.version} version={version} onSelect={this.clickHandler(index)}/>);
                     })}
                    </tbody>
                </table>
                <hr />
                <div dangerouslySetInnerHTML={this.getHtmlView()}></div>
            </div>
        );
    }
}
