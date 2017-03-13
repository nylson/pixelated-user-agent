var CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = new CopyWebpackPlugin([
  { context: 'src/login/', from: '*.html' },
  { context: 'src/login/', from: '*.css' },
  { context: 'src/interstitial/', from: '*' },
  { context: 'app/', from: 'fonts/*' },
  { context: 'app/', from: 'locales/**/*' },
  { context: 'app/', from: 'images/**/*' }
]);
