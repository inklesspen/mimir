import React from 'react';
import {Route, IndexRoute} from 'react-router';
import Home from "./components/Home.jsx";
import WriteupDetail from './components/WriteupDetail.jsx';
import PostDetail from './components/PostDetail.jsx';
import VersionEditor from './components/VersionEditor.jsx';
import {ThreadPage} from './components/ThreadPage.jsx';
import appdata from './appdata';

/*
 * /
 * /threads/:id/page/:page
 * /writeup/:id
 * /writeup/:id/post/:postIndex
 * /editor/:id
 */

export var routes = (
  <Route path={appdata.get('rootUrl')}>
      <IndexRoute component={Home} />
      <Route component={ThreadPage} onEnter={ThreadPage.onEnter} path="threads/:id/page/:page" />
      <Route component={WriteupDetail} onEnter={WriteupDetail.onEnter} path="writeup/:id" />
      <Route component={PostDetail} onEnter={PostDetail.onEnter} path="writeup/:writeupId/post/:postIndex" />
      <Route component={VersionEditor} onEnter={VersionEditor.onEnter} path="editor/:id" />
  </Route>
);
