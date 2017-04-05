let net = require('net');
let readline = require('readline');
let Logging = require('js-logging');
let program = require('commander');

let logger = new Logging();

newClient = function(){
	 program
    .version('0.0.1')
    .option('-p, --port <>', 'Port as argument', parseInt)
    .option('-i, --ip <>', 'IP as argument', String)
    .option('-fn, --firstNumber <>', 'First Number', parseInt)
    .option('-sn, --secondNumber <>', 'Second Number', parseInt)
    .parse(process.argv);
     let client = new net.Socket();
     let logger = new Logging();
     return client
}

let client = newClient()

const ip = program.ip;
const port = program.port;
let numbers;

client.connect(port, ip, function(data) {
 	numbers = String(program.firstNumber) + " " + String(program.secondNumber);
 	client.write(numbers);
});

client.on('data', function(data) {
	logger.info('Received: ' + data);
	numbers = numbers.split(" ")
	let sum = String(parseInt(numbers[0]) + parseInt(numbers[1]));
	if (sum == data)
		logger.info('verified');
	client.destroy(); 
});

client.on('close', function() {
	logger.info('Connection closed');
}); 
