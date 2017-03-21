// jshint esversion: 6

const net = require('net');
const readLine = require('readline');

const client = new net.Socket();

const host = '127.0.0.1';
const port = 3000;
var ans;

function inputFunction() {
  var read = readLine.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  read.question(`Enter the numbers seperated by a space: `, (numbers) => {
        client.write(`${numbers}`);
        numbers = numbers.split(' ');
        ans = Number(numbers[0]) + Number(numbers[1]);
        read.close();
  });
}

client.connect(port, host, () => {
    console.log(`Connected to server at: ${host}:${port}`);
    inputFunction();
});

client.on('data', (data) => {
    data = JSON.parse(data.toString());
    if(data.success === 'true') {
      if(Number(data.message) === ans) {
        console.log(`Status: Success, Ans: ${data.message}`);
      } else {
        console.log(`Status: Wrong Answer. Server returned wrong ans ${data.message}. Correct ans: ${ans}.`);
      }
      client.destroy();
    } else {
      console.log(`Status: Error, ${data.message}`);
        inputFunction();
    }
});

client.on('close',() => {
    console.log(`Connection closed`);
});
