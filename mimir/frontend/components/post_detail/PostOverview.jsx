import React from 'react';
import Immutable from 'immutable';
import {FormRowInput, FormRowCheckbox, FormRowSelect} from '../FormRowTools.jsx';
import PostActions from '../../actions/PostActions';

function mapWithDefaults(post) {
    let map = Immutable.Map({
        'author': '',
        'index': 0,
        'ordinal': '',
        'title': ''
    });
    map = map.merge(post);
    return map;
}


export class PostOverview extends React.Component {
    constructor(props) {
        super(props);
        this.state = this.resetState(props);
    }

    resetState(props) {
        const creating = !props.post;
        return {
            creating,
            // editable by default if creating
            editable: creating,
            post: mapWithDefaults(props.post)
        };
    }

    edit() {
        this.setState({editable: true});
    }

    save() {
        let value = this.state.post.toJS();
        PostActions.savePost(value);
    }

    cancel() {
        // TODO: if 'creating', transition back to the writeup detail
        this.setState(
            {
                editable: false,
                post: mapWithDefaults(this.props.post)
            }
        );
    }

    changeHandler(field) {
        return (value) => {
            this.setState({post: this.state.post.set(field, value)});
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
        // TODO: if creating, optionally take a url to the post on SA
        return (
            <div className="row">
                <div className="col-md-12">
                    <form className="form-horizontal">
                        <FormRowInput editable={this.state.editable} label="Author" value={this.state.post.get('author')} data-id='author' onChange={this.changeHandler('author')} />
                        <FormRowInput editable={this.state.editable} label="Ordinal" value={this.state.post.get('ordinal')} data-id='ordinal' onChange={this.changeHandler('ordinal')} />
                        <FormRowInput editable={this.state.editable} label="Title" value={this.state.post.get('title')} data-id='title' onChange={this.changeHandler('title')} />
                        <FormRowCheckbox editable={this.state.editable} label="Published" value={this.state.post.get('published')} onChange={this.changeHandler('published')} />

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
