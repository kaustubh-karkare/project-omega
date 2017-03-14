/**
 * Parser Object to Parse Argv
 */
function Parser() {
	this.arguments = [];
	this.options = [];
	this.commands = [];
	this._group = 0;
	this._groupCommand = "";
}

/**
 * Add Argument to Parser. Default Datatype is String(0), Int is 1
 * Required is default false.
 */
Parser.prototype.addArgumentWithShortname = function(name,shortname,description,argOpts) {
	var argument = {};
	argument.name = name;
	argument.shortname = shortname;
	argument.description = description||'';
	argument.dataFlag = (typeof argOpts.isDataVar === 'undefined') ? false : argOpts.isDataVar;
	argument.dataType = (typeof argOpts.dataType === 'undefined') ? 0 : argOpts.dataType;
	argument.required = (typeof argOpts.isRequired === 'undefined') ? false : argOpts.isRequired;
	argument.group = (typeof argOpts.group === 'undefined') ? 0 : argOpts.group;
	this.arguments.push(argument);
};

//Add Argument without Shortname
Parser.prototype.addArgument = function(name,description,argOpts) {
	this.addArgumentWithShortname(name,null,description,argOpts)
};

Parser.prototype.printHelp = function() {
	console.log("Usage Information: program [options]"  );
	console.log("Options:");
	this.arguments.forEach(function(argument){
		console.log(argument.name + ": " + argument.description);
	});
};

Parser.prototype.parse = function(argv) {
	//Split into arg and value if "=" exists
	var self = this;
	var args = [];
	var values = [];
	argv.forEach(function(arg){
		var data = arg.split("=");
		args.push(data[0]);
		values.push(data[1]);
	});
	//Parse the argv while checking for each Option
	this.arguments.forEach(function(argument){
		if (
			args.indexOf(argument.name)!=-1 || 
			(
				argument.shortname!=null && 
				args.indexOf(argument.shortname)!=-1
			)
		) {
			//Check for mutually Exclusive groups
			if (argument.group != 0 && self._group == 0) {
				self._group = argument.group;
				self._groupCommand = argument.name;
			}else if (argument.group != self._group) {
				console.error("Error: Options " + argument.name + " & " + self._groupCommand + " cannot be used together.");
				process.exit(1);
			}
			//Check and assign value
			var index = args.indexOf(argument.name);
			if (index == -1) {
				index = args.indexOf(argument.shortname);
			}
			var value = values[index];
			//Check for Integer Datatype
			if (argument.dataFlag && argument.dataType == 1) {
				value = parseInt(value);
				//Throw Error and Exit if NaN
				if (isNaN(value)) {
					console.error("Error: Argument " + argument.name + " must have an Integer Value");
					process.exit(1);
				}
			}
			self.options[argument.name.replace(/-/g,"")] = {};
			self.options[argument.name.replace(/-/g,"")].flag = true;
			self.options[argument.name.replace(/-/g,"")].value = value;
		}else if (argument.required == true) {
			console.error("Error: Argument " + argument.name + " Missing");
			process.exit(1);
		}
	});
	//Check for Commands
	args.forEach(function(arg){
		if (!arg.startsWith("-") && !arg.startsWith("/")) {
			self.commands.push(arg);
		}
	});
};

module.exports = new Parser();
