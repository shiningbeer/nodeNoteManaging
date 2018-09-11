var {sdao} = require('../util/dao')
var jwt = require('jwt-simple')
var { logger } = require('../util/logger')
const results = {
    get: async (req, res) => {
        var { taskId, skip, limit } = req.body
        logger.debug(req.body)
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
    results
}