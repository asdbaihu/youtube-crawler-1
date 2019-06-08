var express      = require('express');
var app          = express();
var http         = require('http').Server(app);
var http2        = require('http').Server(app);
var http3        = require('http').Server(app);
var sio          = require('socket.io');
var psio         = sio(http2);
var csio         = sio(http3);
var EventEmitter = require('events');
EventEmitter.defaultMaxListeners = 20;
var events       = new EventEmitter();

// GLOBALS
var SERVER_PORT  = 8880;
var SCRIPT_PORT  = 9998;
var CLIENT_PORT  = 9999;
var files        = {}

// To make other files accessible
app.use(express.static(__dirname));
// If path doesn't exists give a message
app.use(function(req, res, next) {
    res.status(404).send("Sorry, that route doesn't exist.");
});

app.get('/', function(req, res) {
	res.sendFile(__dirname + '/index.html');
});

csio.on('connection', function(socket){
    console.log("A user is connected to server.");

    socket.on('link', function(data) {
        if (data) {
            events.emit('link', data);
        }
    });

    socket.on('delete-files', function(data) {
        events.emit("delete-files", data);
    });

    socket.on('disconnect', function(data){
        events.emit("delete-files", files[socket.id]);
        delete files[socket.id];
    })

    events.on('output', function(data) {
        socket.emit('output', data);
    });

    events.on('file-info', function(data) {
        if (socket.id in files){
            files[socket.id].push(data);
        }
        else{
            files[socket.id] = [data];
        }
        socket.emit('file-info', data);
    });
});

psio.on('connection', function(socket) {
    console.log("Connected to python script.");

    socket.on('output', function(data) {
        events.emit('output', data);
    });

    socket.on('file-info', function(data) {
        events.emit('file-info', data);
    });

    events.on('link', function(data) {
        socket.emit('link', data);
    });

    events.on('delete-files', function(data) {
        socket.emit('delete-files', data);
    });
});

// LISTENING PORTS
http.listen(SERVER_PORT, function() {
	console.log('server is listening on *:' + SERVER_PORT);
});

http2.listen(SCRIPT_PORT, function() {
	console.log('listening for python script on *:' + SCRIPT_PORT);
});

http3.listen(CLIENT_PORT, function() {
	console.log('listening for client side on *:' + CLIENT_PORT);
});

