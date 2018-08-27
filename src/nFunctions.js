var fs = require('fs')
var dbo = require('./nDbo')

var jwt = require('jwt-simple')
var moment = require('moment')


const connectDB = (callback) => {
  dbo.connect("mongodb://localhost:27017", 'nodeDBDev2', callback)
}

const myMiddleWare = {
  verifyToken: (req, res, next) => {
    //中间件总是执行两次，其中有一次没带上我的数据，所以忽略掉其中一次
    if (req.get('access-control-request-method') == null) {
      if (req.originalUrl != '/task/syncTask')
        console.log(req.originalUrl + ' has been accessed by %s at %s', req.ip, moment(Date.now()).format('YYYY-MM-DD HH:mm'))
      if (req.originalUrl != '/user/gettoken') {
        var token = req.get('token')
        let tokenContainedInfo
        try {
          tokenContainedInfo = jwt.decode(token, 'whatistoken')
        } catch (e) {
          console.log('token wrong!')
          return res.sendStatus(401)
        }
        req.tokenContainedInfo = tokenContainedInfo
      }
    }
    next()
  },
}

const user = {
  getToken: (req, res) => {
    var user = req.body.username
    var pw = req.body.password
    if (user == null || pw == null)
      return res.sendStatus(415)
    if (user == 'bayi' && pw == 'laoye') {
      var token = jwt.encode({
        admin: false
      }, 'whatistoken');
      res.json(token)
    } else if (user == 'superbayi' && pw == 'laoye') {
      var token = jwt.encode({
        admin: true
      }, 'whatistoken');
      res.json(token)
    } else
      return res.sendStatus(401)
  },
  add: () => { },
  delete: () => { },
}

const zmapTask = {
  add: (req, res) => {
    var {taskId,port,ipRange,paused} = req.body
    if (taskId==null||port==null||ipRange==null||paused==null)
      return res.sendStatus(415)
    
    var newtask = {
      taskId,
      port,
      ipRange,
      paused,
      goWrong:false,
      progress:0,
      complete:false,
      running: false,
    }
    dbo.insertCol('zmapTask', newtask, (err, rest) => { })
    res.sendStatus(200)
  },
  delete: (req, res) => {
    var taskId = req.body.taskId
    if (taskId == null)
      return res.sendStatus(415)
    dbo.deleteCol('zmapTask', { taskId }, (err, rest) => { })
    dbo.dropCol(taskId + '--zr', (err, rest) => { })
    res.sendStatus(200)
  },
  syncCommand: (req, res) => {
    var { taskId, paused, } = req.body
    if (taskId == null || paused == null)
      return res.sendStatus(415)
    var update = {
      paused,
      goWrong: false
    }
    dbo.updateCol('zmapTask', { taskId }, update, (err, rest) => {
      err ? res.sendStatus(500) : res.sendStatus(200)
    })
  },
  syncProgress: async (req, res) => {
    console.log(req.body)
    var { taskId } = req.body
    var syncInfo = await new Promise((resolve, reject) => {
      dbo.findoneCol('zmapTask', { taskId }, (err, rest) => {
        resolve(rest)
      })
    })
    var taskResult = await new Promise((resolve, reject) => {
      dbo.findCol(taskId + '--zr', { sent: false }, (err, rest) => {
        resolve(rest)
      })
    })
    var latestResult = []
    for (var r of taskResult) {
      latestResult.push(r.ip)
    }
    var syncResult = {
      goWrong: syncInfo.goWrong,
      progress: syncInfo.progress,
      complete: syncInfo.complete,
      running: syncInfo.running,
      latestResult,
    }
    //mark the result is sent
    for (var r of taskResult) {
      await new Promise((resolve, reject) => {
        console.log(r._id)
        dbo.updateCol(taskId + '--zr', { _id: r._id }, { sent: true }, (err, rest) => {
          resolve(rest)
        })
      })
    }
    if (syncInfo.complete) {
      //delete the task and its result.
    }
    res.json(syncResult)

  },
}

const task = {
  getResult: (req, res) => {
    let {
      nodeTaskId,
      skip,
      limit
    } = req.body
    if (nodeTaskId == null || skip == null || limit == null)
      return res.sendStatus(415)
    dbo.result.getLimit(nodeTaskId, skip, limit, (err, result1) => {
      dbo.result.getCount(nodeTaskId, (err, result2) => {
        let result = { count: result2, samples: result1 }
        console.log(err)
        err ? res.sendStatus(500) : res.json(result)
      })
    })
  },

  syncTask: (req, res) => {
    dbo.task.get_unSync_tasks(async (err, result) => {
      if (err)
        res.sendStatus(500)
      else {
        for (var task of result) {
          delete task.scanRange
          delete task.zmapRange

          var zmapResult = await new Promise((resolve, reject) => {
            dbo.result.getZmapUnsentResult(task.nodeTaskId + 'zr', (err, result2) => {
              var zmapResult = []
              if (err)
                res.sendStatus(500)
              else {
                for (var ip of result2) {
                  zmapResult.push(ip.ip)
                }
                resolve(zmapResult)
              }
            })
          })
          task.zmapResult = zmapResult

        }
        res.json(result)
        dbo.task.mark_sync_complete((err, result) => { })
      }
    })
  },
}

const uploadDir = './uploadPlugins/'
const plugin = {
  add: (req, res) => {
    var file = req.file
    try {
      fs.renameSync(uploadDir + file.filename, uploadDir + file.originalname)
    } catch (e) {
      console.log(e)
      return res.sendStatus(500)
    }
    res.sendStatus(200)
  },
  delete: (req, res) => {
    var pluginName = req.body.pluginName
    if (pluginName == null)
      return res.sendStatus(415)
    fs.unlink(uploadDir + '/' + pluginName, (err, rest) => {
      err ? res.sendStatus(500) : res.sendStatus(200)
    })
  },
  ifHave: () => { },
  get: (req, res) => {
    let plugins
    try {
      plugins = fs.readdirSync(uploadDir)
    } catch (e) {
      return res.sendStatus(500)
    }
    res.json(plugins)
  },
  uploadDir
}

const setting = {
  add: (req, res) => {
    var key = req.body.key
    var value = req.body.value
    if (key == null || value == null)
      return res.sendStatus(415)
    dbo.setting.add(key, value, (err, rest) => {
      err ? res.sendStatus(500) : res.sendStatus(200)
    })
  },
  delete: (req, res) => {
    var key = req.body.key
    if (key == null)
      return res.sendStatus(415)
    dbo.setting.del(key, (err, rest) => {
      err ? res.sendStatus(500) : res.sendStatus(200)
    })
  },
  update: (req, res) => {
    var key = req.body.key
    var value = req.body.value
    if (key == null || value == null)
      return res.sendStatus(415)
    dbo.setting.update(key, value, (err, rest) => {
      err ? res.sendStatus(500) : res.sendStatus(200)
    })
  },
  get: (req, res) => {
    dbo.setting.get((err, result) => {
      err ? res.sendStatus(500) : res.json(result)
    })
  },
}


module.exports = {
  myMiddleWare,
  user,
  plugin,
  setting,
  connectDB,

  //new
  zmapTask,

  //old  
  // task,


}