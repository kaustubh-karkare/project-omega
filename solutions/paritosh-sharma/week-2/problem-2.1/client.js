// jshint esversion: 6, node: true

"use strict";
const net = require('net');
const readLine = require('readline');
const host = '127.0.0.1';
const port = 3000;
let ans;


function inputFunction(client) {
  var read = readLine.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  read.question(`Enter the numbers seperated by a space: `, (inputString) => {
    if (client.writable) {
      client.write(inputString);
    } else client.destroy();
    inputString = inputString.split(' ');
    ans = Number(inputString[0]) + Number(inputString[1]);
    read.close();
  });
}


function connectToServer() {
  const client = new net.Socket();
  let serverActive = false;
  client.connect(port, host, () => {
      console.log(`Connected to server at: ${host}:${port}`);
      serverActive = true;
      inputFunction(client);
  });

  client.on('data', (data) => {
    data = JSON.parse(data.toString());
      if (data.success === true) {
        if (Number(data.message) === ans) {
          console.log(`Success. Ans: ${data.message}`);
        } else {
          console.log(`Wrong Answer. Server returned wrong ans ${data.message}. Correct ans: ${ans}.`);
        }
        client.destroy();
      } else {
        console.log(`Error: ${data.message}`);
          inputFunction(client);
      }
  });

  client.on('error', (error) => {
    console.log('Connection Error');
    serverActive = false;
  });

  client.on('close',() => {
    if (serverActive === false) {
      console.log('Attempting to reconnect...');
      setTimeout( () => {
        connectToServer();
      }, 2000);
    } else {
      console.log(`Connection closed`);
    }
  });
}

connectToServer();
