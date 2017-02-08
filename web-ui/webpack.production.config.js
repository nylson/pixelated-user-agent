var path = require('path');
var webpack = require('webpack');
var copyWebpack = require('./config/copy-webpack');
var loaders = require('./config/loaders-webpack');
var aliases = require('./config/alias-webpack');

module.exports = {
  entry: {
    app: './app/js/index.js',
    account_recovery: './src/account_recovery/index.js',
    sandbox: './app/js/sandbox.js'
  },
  node: { fs: 'empty' },
  output: {
    path: path.join(__dirname, 'dist'),
    filename: '[name].js',
    publicPath: '/assets/'
  },
  resolve: {
    alias: aliases,
    extensions: ['', '.js']
  },
  module: {
    loaders: loaders
  },
  plugins: [
    new webpack.optimize.UglifyJsPlugin(),
    new webpack.optimize.DedupePlugin(),
    copyWebpack
  ]
}
