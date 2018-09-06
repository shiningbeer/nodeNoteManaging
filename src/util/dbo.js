var mongo = require('mongodb').MongoClient
var ObjectId = require('mongodb').ObjectId
var dbo


//connect
var connect = (url, dbname, callback) => {
    mongo.connect(url, (err, db) => {
        dbo = db.db(dbname)
        callback(err)
    })
}

var dropCol = (col, callback) => {
    dbo.collection(col).drop((err, rest) => {
        callback(err, rest)
    })
}


var insertCol = (col, insobj, callback) => {

    if (insobj._id != null) {
        insobj._id = ObjectId(insobj._id)
    }
    dbo.collection(col).insertOne(insobj, (err, rest) => {
        callback(err, rest)
    })
}

var updateCol = (col, where, update, callback) => {
    if (where._id != null)
        where._id = ObjectId(where._id)
    var updatestr = { $set: update }
    dbo.collection(col).updateMany(where, updatestr, (err, rest) => {
        callback(err, rest)
    })
}
var pushCol = (col, where, pushstr, callback) => {
    if (where._id != null)
        where._id = ObjectId(where._id)
    var updatestr = {
        $push: pushstr
    }
    dbo.collection(col).updateMany(where, updatestr, (err, rest) => {
        callback(err, rest)
    })
}

var deleteCol = (col, where, callback) => {
    if (where._id != null)
        where._id = ObjectId(where._id)
    dbo.collection(col).deleteMany(where, (err, rest) => {
        callback(err, rest)
    })
}

var findoneCol = (col, where = {}, callback) => {
    if (where._id != null)
        where._id = ObjectId(where._id)
    dbo.collection(col).findOne(where, (err, result) => {
        callback(err, result)

    });
}
var findlimitCol = (col, where = {}, limit, callback) => {
    if (where._id != null)
        where._id = ObjectId(where._id)
    dbo.collection(col).find(where).limit(limit).toArray((err, result) => {
        callback(err, result)
    });

}
var findFieldCol = (col, where = {}, field, callback) => {
    if (where._id != null)
        where._id = ObjectId(where._id)
    dbo.collection(col).find(where, field).toArray((err, result) => {
        callback(err, result)
    });

}
var findSkipLimitCol = (col, where = {}, skip, limit, callback) => {
    if (where._id != null)
        where._id = ObjectId(where._id)
    dbo.collection(col).find(where).skip(skip).limit(limit).toArray((err, result) => {
        callback(err, result)
    });

}
var findCol = (col, where = {}, callback) => {
    if (where._id != null)
        where._id = ObjectId(where._id)
    dbo.collection(col).find(where).toArray((err, result) => {
        callback(err, result)
    });

}
var getCount = (col, where = {}, callback) => {
    if (where._id != null)
        where._id = ObjectId(where._id)
    dbo.collection(col).find(where).count((err, result) => {
        callback(err, result)
    });

}


module.exports = {
    //new 
    connect,
    dropCol,
    findlimitCol,
    insertCol,
    findoneCol,
    updateCol,
    deleteCol,
    findCol,
    pushCol,
    getCount,
    findFieldCol,
    findSkipLimitCol
}