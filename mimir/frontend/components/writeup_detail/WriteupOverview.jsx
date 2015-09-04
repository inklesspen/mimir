import React from 'react/addons';
import Immutable from 'immutable';
import WriteupActions from '../../actions/WriteupActions';
import {FormRowInput, FormRowCheckbox, FormRowSelect} from '../FormRowTools.jsx';


function mapWithDefaults(detail) {
    let map = Immutable.Map({
        'title': '',
        'author_slug': '',
        'writeup_slug': '',
        'status': 'ongoing',
        'published': false,
        'offensive_content': false,
        'triggery_content': false
    });
    map = map.merge(detail);
    return map;
}


export default class WriteupOverview extends React.Component {
    constructor(props) {
        super(props);
        this.state = this.resetState(props);
    }

    resetState(props) {
        const creating = !props.detail;
        return {
            creating,
            // editable by default if creating
            editable: creating,
            detail: mapWithDefaults(props.detail)
        };
    }

    edit() {
        this.setState({editable: true});
    }

    save() {
        let value = this.state.detail.toJS();
        WriteupActions.saveWriteup(value);
    }

    cancel() {
        this.setState(
            {
                editable: false,
                detail: mapWithDefaults(this.props.detail)
            }
        );
    }

    changeHandler(field) {
        return (value) => {
            this.setState({detail: this.state.detail.set(field, value)});
        };
    }

    componentWillReceiveProps(nextProps) {
        this.setState(this.resetState(nextProps));
    }

    render() {
        let btns;
        if (this.state.editable) {
            btns = (
                <div className="btn-group" role="group">
                    <button type="button" className="btn btn-success" onClick={this.save.bind(this)}>Save</button>
                    <button type="button" className="btn btn-danger" onClick={this.cancel.bind(this)}>Cancel</button>
                </div>
            );
        } else {
            btns = (<button type="button" onClick={this.edit.bind(this)} className="btn btn-default" >Edit</button>);
        }
        // I am not happy with this.
        return (
            <div className="row">
                <div className="col-md-12">
                    <form className="form-horizontal">
                        <FormRowInput editable={this.state.editable} label="Title" value={this.state.detail.get('title')} data-id='title' onChange={this.changeHandler('title')} />
                        <FormRowInput editable={this.state.editable && this.state.creating} label="Author Slug" placeholder="(Cannot be changed later)" value={this.state.detail.get('author_slug')} onChange={this.changeHandler('author_slug')} data-id='author_slug' />
                        <FormRowInput editable={this.state.editable && this.state.creating} label="Writeup Slug" placeholder="(Cannot be changed later)" value={this.state.detail.get('writeup_slug')} onChange={this.changeHandler('writeup_slug')} data-id='writeup_slug' />
                        <FormRowSelect editable={this.state.editable} label="Status" value={this.state.detail.get('status')} data-id='status' onChange={this.changeHandler('status')}>
                            {['Ongoing', 'Abandoned', 'Completed'].map(l => (<option key={l} value={l.toLowerCase()}>{l}</option>))}
                        </FormRowSelect>
                        <FormRowCheckbox editable={this.state.editable} label="Published" value={this.state.detail.get('published')} onChange={this.changeHandler('published')} />
                        <FormRowCheckbox editable={this.state.editable} label="Offensive Content" value={this.state.detail.get('offensive_content')} onChange={this.changeHandler('offensive_content')} />
                        <FormRowCheckbox editable={this.state.editable} label="Triggery Content" value={this.state.detail.get('triggery_content')} onChange={this.changeHandler('triggery_content')} />

                        <div className="form-group">
                            <div className="col-sm-offset-2 col-sm-10">
                                {btns}
                            </div>
                        </div>
                    </form>

                </div>
            </div>
        );
    }
}
