import React from 'react';
import AltContainer from 'alt/AltContainer';
import {VersionStore} from '../stores/VersionStore';
import VersionActions from '../actions/VersionActions';
import Immutable from 'immutable';


const formRowWrapper = function(htmlFor, label, elem) {
    const labelEl = label ? (<label className="control-label" htmlFor={htmlFor}>{label}</label>) : null;
    return (
        <div className="form-group">
            {labelEl}
            {elem}
        </div>
    );
};

class FormInput extends React.Component {
    onChange(event) {
        let value = event.target.value;
        this.props.onChange(value);
    }

    render() {
        // TODO: allow id to be autogenerated if not passed in
        let id = 'FormRow-' + this.props['data-id'];
        let field = (<input type="text" className="form-control input-sm" id={id} value={this.props.value} onChange={this.onChange.bind(this)}/>);
        return formRowWrapper(id, this.props.label, field);
    }
}


class FormTextArea extends React.Component {
    onChange(event) {
        let value = event.target.value;
        this.props.onChange(value);
    }

    render() {
        // TODO: allow id to be autogenerated if not passed in
        let id = 'FormRow-' + this.props['data-id'];
        let field = (<textarea className="form-control" rows="20" id={id} value={this.props.value} onChange={this.onChange.bind(this)} />);
        return field;
    }
}


class VersionForm extends React.Component {
    constructor(props) {
        super(props);

        this.state = this.makeState(props);
    }

    makeState(props) {
        var state = {};
        state.data = Immutable.Map({
            editSummary: '',
            html: props.version.html
        });
        return state;
    }
    componentWillReceiveProps(nextProps) {
        this.setState(this.makeState(nextProps));
    }
    changeHandler(field) {
        return (value) => {
            this.setState({data: this.state.data.set(field, value)});
        };
    }

    render() {
        return (
            <div>
                <FormInput data-id="editSummary" label="Edit Summary" value={this.state.data.get('editSummary')} onChange={this.changeHandler('editSummary')} />
                <FormTextArea data-id="html" value={this.state.data.get('html')} onChange={this.changeHandler('html')} />
            </div>
        );
    }
}


export default class VersionEditor extends React.Component {
    static willTransitionTo(transition, params, query, callback) {
        const wpvId = parseInt(params.id, 10);
        if (isNaN(wpvId)) {
            return callback(wpvId);
        }
        var p = VersionStore.fetchVersion(wpvId);
        p.then(() => {callback(); }).catch((error) => {callback(error.message); });
    }

    render() {
        /*
         * If this.name === 'new-version', the PostStore will be empty.
           In this case, we need to collect the url.
         */
        return (
            <div className="container">
                <AltContainer store={VersionStore}>
                    <VersionForm version={this.props.version} />
                </AltContainer>
            </div>
        );
    }
}
