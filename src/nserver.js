var express = require('express')
var bodypaser = require('body-parser')
var multer = require('multer')
const { user } = require('./modules/user')
const { task } = require("./modules/task")
const { plugin } = require("./modules/plugin")
const { connect } = require("./util/dbo")
const { myMiddleWare } = require('./modules/middleware')
var { logger } = require('./util/logger')
var { results } = require('./modules/results')

var app = express()
app.use(bodypaser.urlencoded({
  extended: false
}))
app.use(bodypaser.json())

app.all('*', myMiddleWare.header);

var upload = multer({
  dest: plugin.uploadDir
})


app.use(myMiddleWare.verifyToken)


app.post('/user/gettoken', user.getToken)
app.post('/user/add', user.add)
app.post('/user/delete', user.delete)

app.post('/task/add', task.add)
app.post('/task/delete', task.delete)
app.post('/task/syncCommand', task.syncCommand)
app.post('/task/syncProgress', task.syncProgress)

app.post('/plugin/add', upload.single('file'), plugin.add)
app.post('/plugin/delete', plugin.delete)
app.post('/plugin/get', plugin.get)
app.post('/plugin/ifHave', plugin.ifHave)
app.post('/pulse', (req, res) => { res.sendStatus(200) })
app.post('/results/get', results.get)

// app.post('/setting/add', setting.add)
// app.post('/setting/delete', setting.delete)
// app.post('/setting/update', setting.update)
// app.post('/setting/get', setting.get)


//start server at localhost on the designated port
var server = app.listen(1911, function () {
  // var host = server.address().address
  // var port = server.address().port

  connect("mongodb://localhost:27017", 'nodeDev2', (err) => {
    err ? logger.info('db connection fail!') : logger.info('node server starts!')
  })

})