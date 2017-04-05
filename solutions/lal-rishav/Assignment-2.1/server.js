let net = require('net');
let readline = require('readline');
let Logging = require('js-logging');
let program = require('commander');

program
  .version('0.0.1')
  .option('-p, --port <>', 'Port as argument', parseInt)
  .option('-i, --ip <>', 'ip as argument', String)
  .parse(process.argv);

let logger = new Logging();
const host = program.ip;
const port = program.port;

let server = net.createServer(function(socket){
	logger.info('Connected: ' + socket.remoteAddress + ':' + socket.remotePort);
	socket.on('data',function(data){

	    data = String(data).split(" ");
		const sum = parseInt(data[0])+parseInt(data[1]);

		setTimeout(function () {
		    socket.write(String(sum)); 
		}, 2000); 

	})

	socket.on('close',function(data){
		logger.info('Connection Closed');
	})
}).listen(port,host);

try{
	server.listen(port,host);
	logger.info('server listining on port ' + port);
}
catch(err){
	logger.info("Connection error");
}

