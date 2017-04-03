let net = require('net');
let readline = require('readline')

let host = '127.0.0.1';
let port = process.argv[2];

net.createServer(function(socket){
	console.log('Connected: '+socket.remoteAddress + ':' + socket.remotePort);
	socket.on('data',function(data){
		let value = parseInt(String(data)[0]) + parseInt(String(data)[2]);
		socket.write(String(value));
	})
	socket.on('close',function(data){
	console.log('CLOSED')
	})
}).listen(port,host);



console.log('server listining on port '+port);
