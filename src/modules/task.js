var { logger } = require('../util/logger')
var dbo = require('../util/dbo')
const task = {
  add: (req, res) => {
    var { taskId, port, ipRange, paused } = req.body
    logger.debug({ taskId })
    if (taskId == null || port == null || ipRange == null || paused == null)
      return res.sendStatus(415)

    var newtask = {
      _id: taskId,
      port,
      ipRange,
      paused,
      goWrong: false,
      progress: 0,
      complete: false,
      running: false,
    }
    dbo.insertCol('task', newtask, (err, rest) => { })
    res.sendStatus(200)
  },
  delete: (req, res) => {
    var taskId = req.body.taskId
    if (taskId == null)
      return res.sendStatus(415)
    dbo.deleteCol('task', { _id: taskId }, (err, rest) => { })
    dbo.dropCol('taskResult--' + taskId, (err, rest) => { res.sendStatus(200) })

  },
  syncCommand: (req, res) => {
    var { taskId, paused, } = req.body
    if (taskId == null || paused == null)
      return res.sendStatus(415)
    var update = {
      paused,
      goWrong: false
    }
    dbo.updateCol('task', { _id: taskId }, update, (err, rest) => {
      err ? res.sendStatus(500) : res.sendStatus(200)
    })
  },
  syncProgress: async (req, res) => {
    logger.debug(req.body)
    var { taskId } = req.body
    var syncInfo = await new Promise((resolve, reject) => {
      dbo.findoneCol('task', { _id: taskId }, (err, rest) => {
        resolve(rest)
      })
    })
    if (syncInfo == null) {
      logger.debug('cant find task with id:%s', taskId)
      res.sendStatus(500)
      return
    }
    var resultCount = await new Promise((resolve, reject) => {
      dbo.getCount('taskResult--' + taskId, {}, (err, rest) => {
        resolve(rest)
      })
    })
    // var latestResult = []
    // for (var r of taskResult) {
    //   latestResult.push(r.ip)
    // }
    var syncResult = {
      goWrong: syncInfo.goWrong,
      progress: syncInfo.progress,
      complete: syncInfo.complete,
      running: syncInfo.running,
      resultCount,
    }
    //mark the result is sent
    // for (var r of taskResult) {
    //   await new Promise((resolve, reject) => {
    //     dbo.updateCol('taskResult--'+taskId, { _id: r._id }, { sent: true }, (err, rest) => {
    //       resolve(rest)
    //     })
    //   })
    // }
    // logger.debug(syncResult)
    res.json(syncResult)

  },
}
module.exports = {
  task,
}