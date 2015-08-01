import React from 'react';
import AltContainer from 'alt/AltContainer';
import {WriteupDetailStore} from '../stores/WriteupStore';

export default class WriteupDetail extends React.Component {
    componentDidMount() {
        WriteupDetailStore.fetchWriteup(this.props.params.id);
    }
    render() {
        return (
            <div className="container">
                Fnord
            </div>
        );
    }
}
