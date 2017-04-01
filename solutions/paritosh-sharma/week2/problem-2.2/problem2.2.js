// jshint esversion: 6, node: true

"use strict";

const fs = require('fs');
const net = require('net');
const path = require('path');
const url = require('url');
const parser = require("./argParser");
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

class httpHeaderParser {

  constructor(headerString) {
    headerString = headerString.substring(headerString.indexOf("\n") + 1);
    headerString = headerString.split('\r\n');
    for(let ii = 0; ii < headerString.length; ii++) {
      let headerStringObj = headerString[ii].split(': ');
      this[headerStringObj[0]] = headerStringObj[1];
    }
  }

  getHeader(headerName) {
    return this[headerName];
  }
}

function download(callback) {

  let client = new net.Socket();
  const file = fs.createWriteStream(filePath, {
    flags: 'a'
  });
  let totalSize, receivedSize = 0;
  let httpHeaderObj = null;
  const progressObj = new downloadProgress();

  client.connect(hostPort, hostName, () => {
    console.log(`Connected to Server`);
    client.write('GET ' + downloadPath + ' HTTP/1.0\r\n\r\n');
  });

  client.on('data', (chunk) => {

    if(httpHeaderObj === null){
      let firstDataChunk = chunk.toString().split('\r\n\r\n');
      httpHeaderObj = new httpHeaderParser(firstDataChunk[0]);
      totalSize = Number(httpHeaderObj.getHeader('Content-Length'));

      if(firstDataChunk[1]) {
        receivedSize += firstDataChunk[1].length;
        progressObj.showProgress(receivedSize, totalSize);
        file.write(firstDataChunk[1]);
      }
    } else {
        receivedSize += chunk.length;
        progressObj.showProgress(receivedSize, totalSize);
        file.write(chunk);
    }
  });

  client.on('end', () => {
    file.end();
  });

  client.on('error', (error) => {
    return callback(`Connection Error`);
  });

  file.on('finish', () => {
    file.close(callback);
  });

  file.on('error', (error) => {
    fs.unlink(filePath);
    return callback(error.message);
  });
}


parser.addArgType({ name: 'String', typeFunction: function(argValue) { return argValue; }, dataType: 'String' });
parser.addArgType({ name: 'Boolean', typeFunction: function(argValue) { return true; }, dataType: 'Boolean' });

parser.addArg({ key: 'dlPath', arg: '--dlPath', type: 'String' });
parser.addArg({ isRequired: true, key: 'dlURL', arg: '--dlURL', type: 'String' });
parser.addArg({ key: 'open', arg: '-o', type: 'Boolean' });
parser.addArg({ key: 'name', arg: '--name', type: 'String' });

const parsedObj = parser.parse();
console.log(parsedObj);
let fileName = parsedObj.dlURL.split('/');
fileName = fileName[fileName.length-1];
fileName = parsedObj.name || fileName;

const filePath = path.join((parsedObj.dlPath || __dirname), fileName);
const hostName = url.parse(parsedObj.dlURL).hostname;
const hostPort = url.parse(parsedObj.dlURL).port || 80;
const downloadPath = url.parse(parsedObj.dlURL).path;

download( (error) => {
  if(error) {
    console.error(error);
    process.exit(1);
  }
  console.log(`\nDownload Completed`);
  if (parsedObj.open === true) {
   console.log(`Opening File`);
   const openFileObj = new openFile(filePath);
   openFileObj.open();
 }
});
