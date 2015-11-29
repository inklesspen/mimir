import React from 'react';
import {Route, create, HistoryLocation, RouteHandler, DefaultRoute} from 'react-router';
import Home from "./components/Home.jsx";
import WriteupDetail from './components/WriteupDetail.jsx';
import PostDetail from './components/PostDetail.jsx';
import {ThreadPage} from './components/ThreadPage.jsx';

/*
 * /
 * /threads/:id/page/:page
 * /extracted/:id
 * /writeup/:id
 * /writeup/:id/post/:postIndex
 * /editor/:id
 */

var routes = ( // location: Router.HistoryLocation
  <Route name="home" handler={RouteHandler} path="/admin/">
      <DefaultRoute handler={Home} />
      <Route name="thread-page" handler={ThreadPage} path="threads/:id/page/:page" />
      <Route name="new-writeup" handler={WriteupDetail} path="writeup/new" />
      <Route name="writeup-detail" handler={WriteupDetail} path="writeup/:id" />
      <Route name="new-post" handler={PostDetail} path="writeup/:writeupId/post/new" />
      <Route name="post-detail" handler={PostDetail} path="writeup/:writeupId/post/:postIndex" />
  </Route>
);

export default create({
    routes,
    location: HistoryLocation
});
