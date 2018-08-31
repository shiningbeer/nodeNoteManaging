
var dbo = require('../util/dbo')
var fs = require('fs')

const uploadDir = './uploadPlugins/'
const plugin = {
  add: (req, res) => {
    var file = req.file
    try {
      fs.renameSync(uploadDir + file.filename, uploadDir + file.originalname)
    } catch (e) {
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

module.exports={
    plugin,
}