let net = require('net');
let readline = require('readline');
let Logging = require('js-logging');
let program = require('commander');

program
  .version('0.0.1')
  .option('-p, --port <n>', 'Port as argument', parseInt)
  .option('-i, --ip <n>', 'ip as argument', String)
  .parse(process.argv);

let logger = new Logging();
let host = program.ip;
let port = program.port;

net.createServer(function(socket){
	logger.info('Connected: '+ socket.remoteAddress + ':' + socket.remotePort);
	socket.on('data',function(data){
		let value = parseInt(String(data)[0]) + parseInt(String(data)[2]);
		socket.write(String(value));
	})
	socket.on('close',function(data){
	logger.info('Connection Closed')
	})
}).listen(port,host);

logger.info('server listining on port '+port);
