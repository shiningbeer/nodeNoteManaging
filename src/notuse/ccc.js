var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({
  host: 'localhost:9200',
  log: 'trace'
});
client.index({
    index: task.taskName, //相当于database
    type:'data',  //相当于table
    body: {
      ip:r.ip,
      data:r.data
    }
  }, (error, response)=>{
    // 
    console.log(error)
    console.log(response)
  });