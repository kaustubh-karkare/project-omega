// jshint esversion: 6, node: true

"use strict";
var net = require('net');

const host = '127.0.0.1';
const port= 3000;

class sum {
  constructor (inputString) {
    inputString = inputString.toString();
    inputString = inputString.split(' ');
    this.firstNumber = inputString[0];
    this.secondNumber = inputString[1];
  }

  calcSum() {
    if (isNaN(this.firstNumber) || isNaN(this.secondNumber)) {
      return (`{ "success": "false", "message": "Invalid data entered. Data must be of type 'Number'." }`);
    } else {
      var ans = Number(this.firstNumber) + Number(this.secondNumber);
      return (`{ "success": true, "message": "${ans}" }`);
    }
  }
}

net.createServer((socket) => {

    console.log(`Connected to client: ${socket.remoteAddress}:${socket.remotePort}`);

    socket.on('data', (data) => {
      console.log(`Received data: ${data.toString()} from ${socket.remoteAddress}:${socket.remotePort}`);
      let sumObj = new sum(data);
      setTimeout(() => {
        socket.write(sumObj.calcSum());
      }, 2000);
    });

    socket.on('close', (data) => {
        console.log(`Disconnected from client: ${socket.remoteAddress}:${socket.remotePort}`);
    });

    socket.on('error', (error) => {
      console.log(error);
    });

}).listen(port, host);

console.log(`Server started on ${host}:${port}`);
