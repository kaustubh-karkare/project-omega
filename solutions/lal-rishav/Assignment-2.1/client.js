let net = require('net');
let readline = require('readline')
let client = new net.Socket();
let port = process.argv[2]
let numbers

client.connect(port, '127.0.0.1', function(data) {
 	numbers = process.argv[3] + " " + process.argv[4];
 	client.write(numbers);
});

client.on('data', function(data) {
	console.log('Received: ' + data);

	if((parseInt(String(numbers)[0])+parseInt(String(numbers)[2])) == data)
		console.log('verified');
	client.destroy(); 
});

client.on('close', function() {
	console.log('Connection closed');
}); 

