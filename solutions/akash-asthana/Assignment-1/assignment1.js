/*Declaration of variables */
var commands = process.argv.slice(2);
var validArguments = ["key", "name", "local", "remote"];
var argumentNameArray = [];
var argumentValueArray = [];
var errorStatement = "";
var errorPresent = false;



/*
* Defining a class for an 
* argument's properties
 */
class Arguments {
    constructor(isReq, type, cantBeUsedWith) {
        this.isReq = isReq;
        this.type = type;
        this.cantBeUsedWith = cantBeUsedWith;
    }
}



/*
* Defining valid arguments as objects 
* with properties like isReq,
* type and cantBeUsedWith
*/
var key = new Arguments(true, "number");
var name = new Arguments(false, "string");
var local = new Arguments(false, "boolean", "remote");
var remote = new Arguments(false, "boolean", "local");



/*
* Function for extracting out 
* argument's name from 
* the commands array
*/
function extractArgumentName(argumentName) {
    var key = "";
    for (var i = 2; i < argumentName.length; i++) {
        if (argumentName[i] === '=') {
            return key;
        }
        key += argumentName[i];
    }
    return key;
}



/*
* Function for extracting out 
* argument's value from 
* the commands array
*/
function extractArgumentValue(argumentName) {
    if (!argumentName.includes("=")) {
        return true;
    }
    var argumentValue = "";
    var index = argumentName.indexOf('=');
    for (var i = index + 1; i < argumentName.length; i++) {
        argumentValue += argumentName[i];
    }
    return argumentValue;
}



/*
* Function to validate the
* type of argument's value
*/
function typeCheck(argumentNameToBeChecked, argumentValueToBeChecked) {
    if (eval(argumentNameToBeChecked).type === "number") {
        return !isNaN(argumentValueToBeChecked);
    }

    if (eval(argumentNameToBeChecked).type === "string") {
        return /^[a-zA-Z]+$/.test(argumentValueToBeChecked);
    }

    if (eval(argumentNameToBeChecked).type === "boolean") {
        return true;
    }
}



/*
* Iterating the commands array
* to extract argument's
* name and value
*/
for (var i = 0; i < commands.length; i++) {

    var argumentName = extractArgumentName(commands[i]);
    var argumentValue = extractArgumentValue(commands[i]);

    //Checking if the argument provided is valid
    if (!validArguments.includes(argumentName)) {
        errorPresent = true;
        errorStatement += `Error : ${argumentName} is undefined`;
        //break;
    }

    argumentNameArray.push(argumentName);
    argumentValueArray.push(argumentValue);
}



/*
* Iterating the validArguments array
* to check if the mandatory
* arguments are present in the
* commands given by the user
*/
for (var i = 0; i < validArguments.length; i++) {
    if (eval(validArguments[i]).isReq == true) {
        if (!argumentNameArray.includes(validArguments[i])) {
            errorStatement += `Error : --${validArguments[i]} argument is required\n`;
            errorPresent = true;
            break;
        }
    }
}



/*
* Iterating the argumentNameArray
* to validate the type of values
* provided by the user
*/
for (i = 0; i < argumentNameArray.length; i++) {
    if (!typeCheck(argumentNameArray[i], argumentValueArray[i])) {
        errorStatement += `Error : Type of ${argumentNameArray[i]} is invalid\n`;
        errorPresent = true;
    }
}



/*
* Iterating the argumentNameArray 
* to check if the arguments provided
* by the user can be used together
*/
for (var i = 0; i < argumentNameArray.length; i++) {
    if (argumentNameArray.includes(eval(argumentNameArray[i]).cantBeUsedWith)) {
        errorStatement += `Error : the --${eval(argumentNameArray[i]).cantBeUsedWith} ` +
            `argument cannot be used with the` +
            `--${argumentNameArray[i]} argument`;
        errorPresent = true;
        break;
    }
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
    console.log(errorStatement)
}


module.exports = { extractArgumentName, extractArgumentValue, typeCheck };

