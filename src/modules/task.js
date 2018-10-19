var { logger } = require('../util/logger')
var { sdao } = require('../util/dao')
const task = {
  add: async (req, res) => {
    var { taskId, port, ipRange, paused, type, plugin } = req.body
    logger.info('[Task]:[add][%s]',taskId)
    if (taskId == null || ipRange == null || paused == null)
      return res.sendStatus(415)

    var newtask = {
      _id: taskId,
      port,
      plugin,
      type,
      ipRange,
      paused,
      goWrong: false,
      progress: 0,
      complete: false,
      running: false,
    }
    await sdao.insert('task', newtask)
    res.sendStatus(200)
  },
  delete: async (req, res) => {
    var taskId = req.body.taskId
    if (taskId == null)
      return res.sendStatus(415)
    logger.info('[Task]:[delete][%s]',taskId)
    await sdao.delete('task', { _id: taskId })
    await sdao.dropCol('taskResult--' + taskId)
    res.sendStatus(200)

  },
  syncCommand: async (req, res) => {
    var { taskId, paused, } = req.body
    if (taskId == null || paused == null)
      return res.sendStatus(415)
    
    logger.info('[Task]:[pause/resume][%s]',taskId)
    var update = {
      paused,
      goWrong: false
    }
    await sdao.update('task', { _id: taskId }, update)
    res.sendStatus(200)
  },
  syncProgress: async (req, res) => {
    var { taskId } = req.body
    logger.info('[Task]:[sync][%s]',taskId)
    var syncInfo = await sdao.findone('task', { _id: taskId })
    if (syncInfo == null) {
      logger.debug('cant find task with id:%s', taskId)
      res.sendStatus(500)
      return
    }
    var resultCount = await sdao.getCount('taskResult--' + taskId, {})
    var syncResult = {
      goWrong: syncInfo.goWrong,
      progress: syncInfo.progress,
      complete: syncInfo.complete,
      running: syncInfo.running,
      resultCount,
    }
    res.json(syncResult)

  },
  getResults: async (req, res) => {
    var { taskId, skip, limit } = req.body
    logger.info('[Task]:[get-result][%s]',taskId)
    if (taskId == null || skip == null || limit == null) {
      return res.sendStatus(415)
    }
    var results = await sdao.findSkipLimit('taskResult--' + taskId, {}, skip, limit)
    let tosend = []
    for (var re of results) {
      tosend.push(re.re)
    }
    res.json(tosend)

  }
}
module.exports = {
  task,
}