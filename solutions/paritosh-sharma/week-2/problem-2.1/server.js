// jshint esversion: 6

var net = require('net');

const host = '127.0.0.1';
const port= 3000;

net.createServer((socket) => {

    console.log(`Connected to client: ${socket.remoteAddress}:${socket.remotePort}`);

    socket.on('data', (data) => {
      console.log(data.toString());
      data = (data.toString()).split(' ');
      setTimeout(() => {
        if(isNaN(data[0]) || isNaN(data[1])) {
          socket.write(`{ "success": "false", "message": "Invalid data entered. Data must be of type 'Number'." }`);
        } else {
          var ans = Number(data[0]) + Number(data[1]);
          socket.write(`{ "success": "true", "message": "${ans}" }`);
        }
      }, 2000);
    });

    socket.on('close', (data) => {
        console.log(`Disconnected from client: ${socket.remoteAddress}:${socket.remotePort}`);
    });

}).listen(port, host);

console.log(`Server started on ${host}:${port}`);
