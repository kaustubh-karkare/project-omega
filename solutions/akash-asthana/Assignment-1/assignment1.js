//Declaration of variables

var commands = process.argv.slice(2);
var argumentNameArray = [];
var argumentValueArray = [];
var errorStatement = "";
var errorPresent = false;


class Parser {

    addOption(name, isReq, type, cantBeUsedWith) {
        this.options.push({ name: name, isReq: isReq, type: type, cantBeUsedWith: cantBeUsedWith });
    }
}
Parser.prototype.options = [];



var parser = new Parser();

parser.addOption(name = "key", isReq = true, type = "number");
parser.addOption(name = "name", isReq = false, type = "string");
parser.addOption(name = "local", isReq = false, type = 'boolean', cantBeUsedWith = "remote");
parser.addOption(name = "remote", isReq = false, type = "boolean", cantBeUsedWith = "local");



/*
* Function for extracting out 
* argument's name from 
* the commands array
*/
function extractArgumentName(argument) {
    var argumentName = "";
    for (var i = 2; i < argument.length; i++) {
        if (argument[i] === '=') {
            return argumentName;
        }
        argumentName += argument[i];
    }
    return argumentName;
}



/*
* Function for extracting out 
* argument's value from 
* the commands array
*/
function extractArgumentValue(argument) {
    if (!argument.includes("=")) {
        return true;
    }
    var argumentValue = "";
    var index = argument.indexOf('=');
    for (var i = index + 1; i < argument.length; i++) {
        argumentValue += argument[i];
    }
    return argumentValue;
}



/*
* Function to check if arguments
* given by the user are defined
*/
function checkIfArgumentDefined(argumentName) {
    for (var i = 0; i < parser.options.length; i++) {
        if (argumentName === parser.options[i].name) {
            return true;
        }
    }
    return false;
}



/*
* Function to validate the
* type of argument's value
*/
function typeCheck(argumentNameToBeChecked, argumentValueToBeChecked) {

    var i;

    for (i = 0; i < parser.options.length; i++) {
        if (argumentNameToBeChecked === parser.options[i].name) {
            argumentNameToBeChecked = parser.options[i].name;
            break;
        }
    }

    if (parser.options[i].type === "number") {
        return !isNaN(argumentValueToBeChecked);
    }
    if (parser.options[i].type === "string") {
        return /^[a-zA-Z]+$/.test(argumentValueToBeChecked);
    }
    if (parser.options[i].type === "boolean") {
        return true;
    }
}



/*
* Function to check if
* the mandatory arguments are
* present in the commands
* given by the user
*/
function areRequiredArgumentsPresent(argumentNameArray) {
    for (var i = 0; i < parser.options.length; i++) {
        if (parser.options[i].isReq === true) {
            if (!argumentNameArray.includes(parser.options[i].name)) {
                errorStatement += `Error :The argument "--${parser.options[i].name}" is required\n`;
                return false;
            }
        }
    }
    return true;
}



/*
* Function to check if arguments 
* given by the user can be used together
*/
function ifArgumentsCanBeUsedTogether(argumentNameArray) {
    for (var i = 0; i < argumentNameArray.length; i++) {
        if (argumentNameArray.includes(parser.options[i].cantBeUsedWith)) {
            errorStatement += `Error : The argument "--${parser.options[i].name}" can't be used with` +
                ` the argument "--${parser.options[i].cantBeUsedWith}"\n`
            return false;
        }
    }
    return true;
}



//MAIN FUNCTION
function parseArgumentsIntoJSON(commands) {

    for (var i = 0; i < commands.length; i++) {

        var argumentName = extractArgumentName(commands[i]);
        var argumentValue = extractArgumentValue(commands[i]);

        //Checking if the argument provided is defined
        if (!checkIfArgumentDefined(argumentName)) {
            errorPresent = true;
            errorStatement += `Error : The argument "--${argumentName}" is undefined`;

        }

        if (!typeCheck(argumentName, argumentValue)) {
            errorStatement += `Error : Type of the argument "--${argumentName}" is invalid\n`;
            errorPresent = true;
        }



        argumentNameArray.push(argumentName);
        argumentValueArray.push(argumentValue);
    }



    /*
    * Checking if the mandatory arguments 
    * are present 
    */
    if (!areRequiredArgumentsPresent(argumentNameArray)) {
        errorPresent = true;
    }


    /*
    * Checking if the arguments 
    * can be used together
    */
    if (!ifArgumentsCanBeUsedTogether(argumentNameArray)) {
        errorPresent = true;
    }



    /*
    * Printing out the JSON output
    * if no error is found
    */
    if (!errorPresent) {
        var finalResult = {};
        for (var i = 0; i < argumentNameArray.length; i++) {
            finalResult[argumentNameArray[i]] = argumentValueArray[i];
        }

        console.log(JSON.stringify(finalResult));
    }

    /*
    * Printing out the error statement 
    * if error is found
    */
    else {
        console.log(errorStatement);
    }


}



/*
* Calling the main function and 
* passing the command given by the user
*/
parseArgumentsIntoJSON(commands);



//Exporting functions to test
module.exports = {
    extractArgumentName,
    extractArgumentValue,
    typeCheck,
    checkIfArgumentDefined,
    areRequiredArgumentsPresent,
    ifArgumentsCanBeUsedTogether,
    parseArgumentsIntoJSON
};
