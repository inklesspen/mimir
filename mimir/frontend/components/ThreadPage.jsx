import React from 'react';
import {Link} from 'react-router';
import jsonrpc from '../util/jsonrpc';
import classNames from 'classnames';
import AltContainer from 'alt/AltContainer';
import {ThreadPageStore} from '../stores/ThreadStore';
import {Breadcrumbs, Breadcrumb} from './Breadcrumbs.jsx';

const EXTRACT_WORKING = 'extract_working';
const EXTRACT_DONE = 'extract_done';


class BooleanSpan extends React.Component {
    render() {
        var classes = classNames("fa", "fa-lg",
                                 (this.props.value ? "fa-check-circle-o" : "fa-times-circle"),
                                 (this.props.value ? "text-info" : "text-danger"));
        return (<span className={classes}></span>);
    }
}

class ThreadPost extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            extractState: null
        };
    }


    extractLink() {
        if (this.state.extractState === EXTRACT_WORKING) {
            return (
                <span>Extracting <span className="fa fa-cog fa-spin"></span></span>
            );
        }
        if (this.state.extractState === EXTRACT_DONE) {
            return (
                <span>Extraction Complete <span className="fa fa-lg fa-check-square-o"></span></span>
            );
        }
        return (
            <a role="button" href="#" onClick={this.clickHandler()}>Extract</a>
        );
    }

    clickHandler() {
        return (evt) => {
            evt.preventDefault();
            this.setState({extractState: EXTRACT_WORKING});
            jsonrpc('extract_post', [this.props.post.id]).then(() => {
                this.setState({extractState: EXTRACT_DONE});
            });
        };
        //jsonrpc('extract_post', [this.props.post.id]);
    }

    getHtmlView() {
        return {
            __html: this.props.post.html
        };
    }

    render() {
        return (
            <div className="panel panel-default">
                <div className="panel-heading">
                    <ul className="list-inline">
                        <li><a href={this.props.post.url}>#{this.props.post.id}</a></li>
                        <li>{this.props.post.author}</li>
                        <li>Extracted <BooleanSpan value={this.props.post.has_been_extracted} /></li>
                        <li>In Writeup <BooleanSpan value={this.props.post.is_in_writeup} /></li>
                        <li className="pull-right">{this.extractLink()}</li>
                    </ul>
                    <span></span>
                </div>
                <div className="panel-body" dangerouslySetInnerHTML={this.getHtmlView()}></div>
            </div>
        );
    }
}


class ThreadPosts extends React.Component {
    pageLink(num) {
        const dest = `/admin/threads/${this.props.threadPage.thread_id}/page/${num}`;
        return (
            <Link to={dest}>{num}</Link>
        );
    }
    pagination() {
        const start = 1;
        const current = this.props.threadPage.page_num;
        const finish = this.props.threadPage.page_count;
        const leftArrowInner = (<span ariaHidden="true">«</span>);
        const leftArrow = (current === start) ? (
            <li className="disabled"><span ariaLabel="Previous">{leftArrowInner}</span></li>
        ) : (
            <li>
                <Link to={`/admin/threads/${this.props.threadPage.thread_id}/page/${start}`} ariaLabel="First">{leftArrowInner}</Link>
            </li>
        );
        const rightArrowInner = (<span ariaHidden="true">»</span>);
        const rightArrow = (current === finish) ? (
            <li className="disabled"><span ariaLabel="Next">{rightArrowInner}</span></li>
        ) : (
            <li>
                <Link to={`/admin/threads/${this.props.threadPage.thread_id}/page/${finish}`} ariaLabel="Last">{rightArrowInner}</Link>
            </li>
        );
        const boxes = [];
        for (let i = current - 2; i < current; i++) {
            if (i < start) {
                continue;
            }
            let box = (
                <li key={i}>{this.pageLink(i)}</li>
            );
            boxes.push(box);
        }
        const rightLength = (4 - boxes.length);
        boxes.push((
            <li className="active" key={current}><a href="#">{current} <span className="sr-only">(current)</span></a></li>
        ));
        for (let i = current + 1; i < (current + 1 + rightLength); i++) {
            if (i > finish) {
                continue;
            }
            let box = (
                <li key={i}>{this.pageLink(i)}</li>
            );
           boxes.push(box);
        }
        return (
            <nav>
                <ul className="pagination">
                    {leftArrow}
                    {boxes}
                    {rightArrow}
                </ul>
            </nav>
        );
    }
    render() {
        if (!this.props.threadPage) {
            return null;
        }
        return (
            <div>
                <div>{this.pagination()}
                </div>
                {this.props.threadPage.posts.map((post, i) => {
                    return (<ThreadPost key={post.id} post={post} pagePost={i + 1} />);
                 })}
            </div>
        );
    }
}


export class ThreadPage extends React.Component {
    static onEnter(nextState, replaceState, callback) {
        const params = nextState.params;
        const threadId = parseInt(params.id, 10);
        if (isNaN(threadId)) {
            return callback(threadId);
        }
        const pageNum = parseInt(params.page, 10);
        if (isNaN(pageNum)) {
            return callback(pageNum);
        }
        var p = ThreadPageStore.fetchThreadPage(threadId, pageNum);
        p.then(function() {
            callback();
        }).catch(function(error) {
            callback(error.message);
        });
    }

    render() {
        const threadId = ThreadPageStore.state.threadPage.thread_id;
        return (
            <div className="container">
                <AltContainer store={ThreadPageStore}>
                    <Breadcrumbs>
                        <Breadcrumb to="/admin/" title="Home" />
                        <Breadcrumb active={true} title={`Thread #${threadId}`} />
                    </Breadcrumbs>
                    <hr />
                    <ThreadPosts />
                </AltContainer>
            </div>
        );
    }
}
