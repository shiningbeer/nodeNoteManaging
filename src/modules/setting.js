
const setting = {
  add: (req, res) => {
    var key = req.body.key
    var value = req.body.value
    if (key == null || value == null)
      return res.sendStatus(415)
  },
  delete: (req, res) => {
    var key = req.body.key
    if (key == null)
      return res.sendStatus(415)
  },
  update: (req, res) => {
    var key = req.body.key
    var value = req.body.value
    if (key == null || value == null)
      return res.sendStatus(415)
  },
  get: (req, res) => {
  },
}
module.exports={
    setting,
}