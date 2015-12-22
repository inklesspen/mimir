var path = require('path');

var sourcePath = path.join(__dirname, 'mimir', 'frontend');
var publicSourcePath = path.join(__dirname, 'mimir', 'lib', 'js');
var assetsPath = path.join(__dirname, 'mimir', 'static');
var publicPath = '/static/';

var commonLoaders = [
  {
    /*
     * TC39 categorises proposals for babel in 4 stages
     * Read more http://babeljs.io/docs/usage/experimental/
     */
    test: /\.jsx$/, loader: "babel-loader?stage=0"
  },
  {
    test: /\.js$/,
    loader: "babel-loader?stage=0",
    include: [sourcePath, publicSourcePath]
  },
  { test: /\.png$/, loader: "url-loader" },
  { test: /\.jpg$/, loader: "file-loader" },
  { test: /\.html$/, loader: "html-loader" }
];

module.exports = {
    // context: sourcePath,
    entry: {
      mimir: path.join(sourcePath, "./App.jsx"),
      public: path.join(publicSourcePath, './main.js')
    },

    output: {
      // The output directory as absolute path
      path: assetsPath,
      // The filename of the entry chunk as relative path inside the output.path directory
      filename: '[name].js',
      // The output path from the view of the Javascript
      publicPath: publicPath

    },
    module: {
      // preLoaders: [{
      //   test: /\.js$|.jsx$/,
      //   exclude: /node_modules/,
      //   loaders: ['eslint']
      // }],
      loaders: commonLoaders
    },
    resolve: {
      modulesDirectories: [
        sourcePath, publicSourcePath, "node_modules"
      ]
    },
    devServer: {
        contentBase: "./mimir/",
        host: '0.0.0.0',
        proxy: {
            "*": {
                "target": {
                    "host": "127.0.0.1",
                    "port": 6543
                }
            }
        }
    }
};
