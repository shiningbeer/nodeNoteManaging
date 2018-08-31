var {logger}=require('../util/logger')
var dbo = require('../util/dbo')
const zmapTask = {
  add: (req, res) => {
    var {taskId,port,ipRange,paused} = req.body
    logger.debug({taskId})
    if (taskId==null||port==null||ipRange==null||paused==null)
      return res.sendStatus(415)
    
    var newtask = {
      _id:taskId,
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
    dbo.deleteCol('zmapTask', { _id:taskId }, (err, rest) => { })
    dbo.dropCol('taskResult--'+taskId, (err, rest) => {res.sendStatus(200) })
    
  },
  syncCommand: (req, res) => {
    var { taskId, paused, } = req.body
    if (taskId == null || paused == null)
      return res.sendStatus(415)
    var update = {
      paused,
      goWrong: false
    }
    dbo.updateCol('zmapTask', { _id:taskId }, update, (err, rest) => {
      err ? res.sendStatus(500) : res.sendStatus(200)
    })
  },
  syncProgress: async (req, res) => {
    console.log(req.body)
    var { taskId } = req.body
    var syncInfo = await new Promise((resolve, reject) => {
      dbo.findoneCol('zmapTask', { _id:taskId }, (err, rest) => {
        resolve(rest)
      })
    })
    if(syncInfo==null){
        logger.debug('cant find task with id:%s',taskId)
      res.sendStatus(500)
      return
    }
    var taskResult = await new Promise((resolve, reject) => {
      dbo.findCol('taskResult--'+taskId, { sent: false }, (err, rest) => {
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
        dbo.updateCol('taskResult--'+taskId, { _id: r._id }, { sent: true }, (err, rest) => {
          resolve(rest)
        })
      })
    }
    logger.debug(syncResult)
    res.json(syncResult)

  },
}
module.exports={
    zmapTask,
}