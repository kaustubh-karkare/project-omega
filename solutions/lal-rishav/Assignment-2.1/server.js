var net = require('net');
var host = '127.0.0.1';
var port = 8080;

net.createServer(function(sock){
	console.log('Connected: '+sock.remoteAddress + ':' +sock.remotePort);
	sock.on('data',function(data){
		var value = parseInt(String(data)[0])+parseInt(String(data)[2]);
		sock.write(String(value));
	})
	sock.on('close',function(data){
	console.log('CLOSED')
})
}).listen(port,host);



console.log('server listining on port '+port);
