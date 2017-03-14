#!/usr/bin/nodejs
var parser = require('./parser');

//Add Random Options
parser.addArgumentWithShortname(
	'--key',
	'-k',
	"Integer Argument",
	{ isDataVar: true, dataType: 1 , isRequired: true}
);
parser.addArgument('--value',"String Argument",{isDataVar: true});
parser.addArgument('--local',"Random Exclusive Argument",{group: 1});
parser.addArgument('--remote',"Random Exclusive Argument",{group: 2});
//Parse the Argv
parser.parse(process.argv);

//Print Key Value JSON
if(parser.options.key && parser.options.key.flag){
	var json = {}
	json.key = parser.options.key.value;
	json.value = "";
	if(parser.options.value && parser.options.value.flag)
		json.value = parser.options.value.value;
	console.log(json);
}
//Print Commands
if(parser.commands.length > 0){
	var json = {};
	json.command = parser.commands[0];
	json.subCommands = parser.commands.slice(1).join(" ");
	console.log(json);
}
