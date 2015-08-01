import React from 'react';
import routes from './routes.jsx';

routes.run((Root) => {
React.render(
  <Root />,
  document.getElementById('ReactApp')
);
});
