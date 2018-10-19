var {logger}=require('../util/logger')
var jwt = require('jwt-simple')

const myMiddleWare = {
  verifyToken: (req, res, next) => {
    //中间件总是执行两次，其中有一次没带上我的数据，所以忽略掉其中一次
    if (req.get('access-control-request-method') == null) {
      if (req.originalUrl != '/task/syncProgress')
        logger.debug('[Acess]:[path%s][IP%s]',req.originalUrl,req.ip)
      if (req.originalUrl != '/user/gettoken') {
        var token = req.get('token')
        let tokenContainedInfo
        try {
          tokenContainedInfo = jwt.decode(token, 'whatistoken')
        } catch (e) {
          logger.error('token wrong!')
          return res.sendStatus(401)
        }
        req.tokenContainedInfo = tokenContainedInfo
      }
    }
    next()
  },
  header:(req, res, next)=> {
    res.header("Access-Control-Allow-Origin", '*');
    res.header("Access-Control-Allow-Headers", "token,content-type,productId,X-Requested-With");
    res.header("Access-Control-Allow-Methods", "PUT,POST,GET,DELETE,OPTIONS");
    res.header("X-Powered-By", ' 3.2.1')
    res.header("Content-Type", "application/json;charset=utf-8");
    next();
}
}
module.exports={
    myMiddleWare,
}