var path = require('path');
var dm = require('mt-files-downloader');

var dm = new dm();


var url = "";
for(var i=2;i<process.argv.length;i++){
	url=url.concat(process.argv[i]);
}
console.log("Your download is started on on the url "+url);
var n="";


for(var i=url.length-1;url[i]!='/';i--){
	
	n=n.concat(String(url[i]));

}
var name= n.split("").reverse().join("");

var path = `C:/Users/Lal rishav/Desktop/project omega/${name}`;//specified location and new is the name of the file;
//the path is only valid if ther is a folder on desktop named project omega else chnage the path location
console.log('The save path for your file is '+path);

var download = dm.download(url,path);
download.on('start',function(){
	console.log('Your download have been started');

})

download.setRetryOptions({
	maxRetries		:10,
	retryInterval	:100
});

download.setOptions({
	threadCount :  3,
	method		: 'GET',
	port 		: 80,
	timeout 	: 5000,
	range 		: '0-100',
});

download.on('error',function(){
	console.log('there is an error in downloading');
	console.log(download.error);
})

download.on('end',function(){
	console.log('Download have been successfully finished');

})

download.start();
