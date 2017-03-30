// jshint esversion: 6, node: true

"use strict";

const parser = require('./argParser');
const fs = require('fs');
const path = require('path');
const net = require('net');
const exec = require('child_process').exec;

class openFile {

  constructor(filePath) {
    this.filePath = filePath;
  }

  getCommandLine() {
     switch (process.platform) {
        case 'darwin' : return 'open';
        case 'win32' : return 'start';
        case 'win64' : return 'start';
        default : return 'xdg-open';
     }
  }

  open() {
      exec(this.getCommandLine() + ' ' + this.filePath);
  }
}

class downloadProgress {

  showProgress(receivedSize, totalSize) {
    let percentage = (receivedSize / totalSize) * 100;
    process.stdout.clearLine();
    process.stdout.cursorTo(0);
    process.stdout.write(`Downloaded: ${receivedSize} bytes of ${totalSize} bytes -  ${Math.ceil(percentage)}%`);
  }

}

function download(callback) {

  let totalSize, receivedSize = 0;
  const file = fs.createWriteStream(filePath);
  const client = new net.Socket();
  const progressObj = new downloadProgress();

  client.connect(80, parsedObj.dlURL, () => {
    console.log(`Connected to server at ${parsedObj.dlURL}`);
  });

  client.on('data', (data) => {
    console.log(data.length());
    data.pipe(file);
  });


  sendReq.on('data', (chunk) => {
    receivedSize += chunk.length;
    progressObj.showProgress(receivedSize, totalSize);
  });

  sendReq.on('error', (error) => {
    fs.unlink(filePath);
    return callback('Connection Error');
  });

  file.on('finish', () => {
    file.close(callback);
  });

  file.on('error', (error) => {
    fs.unlink(filePath);
    return callback(error.message);
  });

}

parser.addArgType({ name: 'String', condition: function(argValue) { return true; }, dataType: 'String', castFunction: function(argValue) { return argValue; } });
parser.addArgType({ name: 'Boolean', condition: function(argValue) { return true; }, dataType: 'Boolean', castFunction: function(argValue) { return true; } });

parser.addArg({ key: 'dlPath', arg: '--dlPath', type: 'String' });
parser.addArg({ isRequired: true, key: 'dlURL', arg: '--dlURL', type: 'String' });
parser.addArg({ key: 'open', arg: '-o', type: 'Boolean' });
parser.addArg({ key: 'name', arg: '--name', type: 'String' });

const parsedObj = parser.parse();

let fileName = parsedObj.dlURL.split('/');
fileName = fileName[fileName.length-1];
fileName = parsedObj.name || fileName;

const filePath = path.join((parsedObj.dlPath || __dirname), fileName);

download((error) => {
  if (error) {
    console.error(error);
    process.exit(1);
  }
  console.log('\nFile downloaded successfully');
  if (parsedObj.open === true) {
    console.log(`Opening File`);
    const openFileObj = new openFile(filePath);
    openFileObj.open();
  }
});
