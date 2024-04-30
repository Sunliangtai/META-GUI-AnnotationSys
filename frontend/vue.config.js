module.exports = {
    devServer: {
        proxy: "http://127.0.0.1:5000"
      },
      publicPath: process.env.NODE_ENV === 'production'
      ? '/static/'
      : '/'
}