import React from 'react';
import {Route, create, HistoryLocation, RouteHandler, DefaultRoute} from 'react-router';
import Home from "./components/Home.jsx";
import WriteupDetail from './components/WriteupDetail.jsx';

var routes = ( // location: Router.HistoryLocation
  <Route name="home" handler={RouteHandler} path="/admin/">
      <DefaultRoute handler={Home} />
      <Route name="new-writeup" handler={WriteupDetail} path="writeup/new" />
      <Route name="writeup-detail" handler={WriteupDetail} path="writeup/:id" />
  </Route>
);

export default create({
    routes,
    location: HistoryLocation
});
