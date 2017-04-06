let net = require('net');
let readline = require('readline');
let Logging = require('js-logging');
let program = require('commander');

let logger = new Logging();

newClient = function() {
	 program
	    .version('0.0.1')
	    .option('-p, --port <>', 'Port as argument', parseInt)
	    .option('-i, --ip <>', 'IP as argument', String)
	    .option('-fn, --firstNumber <>', 'First Number', parseInt)
	    .option('-sn, --secondNumber <>', 'Second Number', parseInt)
	    .parse(process.argv);
	    let client = new net.Socket();
	    return client;
}

sendNumbers = function(firstNumber,secondNumber,client) {
    numbers = String(firstNumber) + " " + String(secondNumber);
	client.write(numbers);
}

verifySum = function(data) {
	logger.info('Received: ' + data);
	numbers = numbers.split(" ");
	let sum = String(parseInt(numbers[0]) + parseInt(numbers[1]));
	if (sum == data)
		logger.info('verified');
}

let client = newClient();
const ip = program.ip;
const port = program.port;
let numbers;

client.connect(port, ip, function(data) {
	sendNumbers(program.firstNumber,program.secondNumber,client) 
});

client.on('data', function(data) {
	verifySum(data);
	client.destroy(); 
});

client.on('close', function() {
	logger.info('Connection closed');
}); 
