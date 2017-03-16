
var argList = [];
var parsedJson = {};

// add aditional argument types here e.g 'Type': 'Conditions on argValue'.
// Enter 'true' if no conditions

argTypeConditions = {
   'String': 'true',
   'Boolean': 'true',
   'Int': '!isNaN(argValue)',
   '+Int': '!isNaN(argValue) && argValue * 1 >= 0' // represents + integers.
};

function argBuilder(key, arg, type, required, position) {
   if (key === null) {
      console.log(`ERROR: Key of argument '${arg}' cannot be null`);
      process.exit(1);
   }
   if (!(type in argTypeConditions)) {
      console.log(`ERROR: Invalid type of argument '${arg}'`);
      process.exit(1);
   }
   var tempObj = {};
   tempObj.key = key;
   tempObj.arg = arg;
   tempObj.type = type;
   tempObj.position = position;
   if (required === 'required')
      tempObj.required = true;
   else if (required === 'notRequired')
      tempObj.required = false;
   else {
      console.log(`ERROR: Invalid require parameter for argumnet '${arg}'`);
      process.exit(1);
   }
   argList.push(tempObj);
}

//argument validator function. Add additional validations here.
//Pass printCheck = true to print parsed arguments.

function argValidator(printCheck) {
   for (i = 0; i < argList.length; i++) {
      if (argList[i].required === true && !(argList[i].key in parsedJson)) {
         console.log(`ERROR: Value of '${argList[i].arg}'  required`);
         return;
      }
   }
   if (printCheck === true)
      printParsedArgs();
}

function printParsedArgs() {
   console.log(parsedJson);
}

function argParser(inputArgs) {
   var  ii, jj, flag, argValue;
   for (ii = 0; ii < inputArgs.length; ii++) {
      var str = inputArgs[ii];
      flag = 0;
      if (str.search('-') !== 0) {
         for (jj = 0; jj < argList.length; jj++) {
            if (argList[jj].position === ii) {
               flag = 1;
               parsedJson[argList[jj].key] = str;
            }
         }
         if (flag === 0) {
            console.log(`ERROR: Invalid argument '${str}' entered`);
            return;
         }
      } else {
         str = str.split('=');
         for (jj = 0; jj < argList.length; jj++) {
            if (argList[jj].arg === str[0]) {
               flag = 1;
               argValue = str[1];
               if (eval(argTypeConditions[argList[jj].type]))  {
                  if (argList[jj].type === 'Boolean')
                     parsedJson[argList[jj].key] = true;
                  else
                     parsedJson[argList[jj].key] = argValue;
               } else {
                  console.log(`ERROR: Invalid value for argument '${argList[jj].arg}'. Must be of type '${argList[jj].type}'`);
                  return;
               }
            }
         }
         if (flag === 0) {
            console.log(`ERROR: Invalid argument '${str[0]}' entered`);
            return;
         }
      }
   }
   argValidator(true);
}

// add new arguments here in the format argBuilder('key', 'argumentName', 'type', 'required/notRequired', position(if necessary));

argBuilder('command', null, 'String', 'notRequired', 0);
argBuilder('subcommand', null, 'String', 'notRequired', 1);
argBuilder('key', '--key', '+Int', 'required');
argBuilder('name', '--name', 'String', 'notRequired');
argBuilder('verbrose', '-v', 'Boolean', 'notRequired');
argBuilder('local', '--local', 'Boolean', 'notRequired');
argBuilder('remote', '--remote', 'Boolean', 'notRequired');

var inputArgs = process.argv.slice(2);

argParser(inputArgs);
