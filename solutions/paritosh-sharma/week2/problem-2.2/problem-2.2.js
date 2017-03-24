// jshint esversion: 6, node: true

"use strict";

const parser = require('./argParser');
const fs = require('fs');
const path = require('path');
const request = require('request');
const exec = require('child_process').exec;

function getCommandLine() {
   switch (process.platform) {
      case 'darwin' : return 'open';
      case 'win32' : return 'start';
      case 'win64' : return 'start';
      default : return 'xdg-open';
   }
}

function showProgress(receivedSize, totalSize) {
  var percentage = (receivedSize / totalSize) * 100;
  process.stdout.clearLine();
  process.stdout.cursorTo(0);
  process.stdout.write(`Downloaded: ${receivedSize} bytes of ${totalSize} bytes -  ${Math.ceil(percentage)}%`);
}

function download(dlURL, dlPath, callback) {

  var totalSize, receivedSize = 0;
  var file = fs.createWriteStream(dlPath);
  var sendReq = request.get(dlURL);

  sendReq.on('response', (response) => {
    if (response.statusCode !== 200) {
        return callback(`ERROR: response Code ${response.statusCode}`);
    }
    totalSize = Number(response.headers[ 'content-length']);
  });

  sendReq.pipe(file);

  sendReq.on('data', (chunk) => {
    receivedSize += chunk.length;
    showProgress(receivedSize, totalSize);
  });
  
  sendReq.on('error', (error) => {
    fs.unlink(dlPath);
    return callback('Connection Error');
  });

  file.on('finish', () => {
    file.close(callback);
  });

  file.on('error', (error) => {
    fs.unlink(dlPath);
    return callback(error.message);
  });

}

parser.addArgType({ name: 'String', condition: function(argValue) { return true; }, dataType: 'String', castFunction: function(argValue) { return argValue; } });
parser.addArgType({ name: 'Boolean', condition: function(argValue) { return true; }, dataType: 'Boolean', castFunction: function(argValue) { return true; } });

parser.addArgGroup({ isRequired: false, argList: [ { key: 'dlPath', arg: '--dlPath', type: 'String', position: null } ] });
parser.addArgGroup({ isRequired: true, argList: [ { key: 'dlURL', arg: '--dlURL', type: 'String', position: null } ] });
parser.addArgGroup({ isRequired: false, argList: [ { key: 'open', arg: '-o', type: 'Boolean', position: null } ] });
parser.addArgGroup({ isRequired: false, argList: [ { key: 'name', arg: '--name', type: 'String', position: null } ] });

var parsedObj = parser.parse();

var fileName = parsedObj.dlURL.split('/');
fileName = fileName[fileName.length-1];
fileName = parsedObj.name || fileName;

var dlPath = path.join((parsedObj.dlPath || __dirname), fileName);

download(parsedObj.dlURL, dlPath, (error) => {
  if (error) {
    console.log(error);
    process.exit(1);
  }
  console.log('\nFile downloaded successfully');
  if (parsedObj.open === true) {
    console.log(`Opening File`);
    exec(getCommandLine() + ' ' + dlPath);
  }
});
