var dbo = require('../util/dbo')
var jwt = require('jwt-simple')
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
module.exports = {
  user,
}