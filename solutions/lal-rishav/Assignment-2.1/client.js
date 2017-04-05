let net = require('net');
let readline = require('readline');
let Logging = require('js-logging');
let program = require('commander');

program
  .version('0.0.1')
  .option('-p, --port <n>', 'Port as argument', parseInt)
  .option('-i, --ip <n>', 'IP as argument', String)
  .option('-fn, --fn <n>', 'First Number', parseInt)
  .option('-sn, --sn <n>', 'SecondNumber', parseInt)
  .parse(process.argv);

let logger = new Logging();
let client = new net.Socket();

let ip = program.ip;
let port = program.port;
let numbers;

client.connect(port, ip, function(data) {
 	numbers = String(program.fn) + " " + String(program.sn);
 	client.write(numbers);
});

client.on('data', function(data) {
	logger.info('Received: ' + data);
	let sum = parseInt(String(numbers)[0])+parseInt(String(numbers)[2]);
	if( sum == data)
		logger.info('verified');
	client.destroy(); 
});

client.on('close', function() {
	logger.info('Connection closed');
}); 
