var net = require('net');
var port = 8080;
var client = new net.Socket();
var a;
client.connect(port, '127.0.0.1', function(data) {
	 a = process.argv[2]+" "+process.argv[3];
	client.write(a);
});

client.on('data', function(data) {
	console.log('Received: ' + data);
	if((parseInt(String(a)[0])+parseInt(String(a)[2]))==(parseInt(String(a)[0])+parseInt(String(a)[2])))
		console.log('verified');
	client.destroy(); // kill client after server's response
});

client.on('close', function() {
	console.log('Connection closed');
});
