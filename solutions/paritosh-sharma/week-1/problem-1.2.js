
var argList = [];

// add aditional argument types here e.g 'Type': function(argValue) [{ return condition; }, 'Data Type'.
// Enter 'true' if no conditions

argTypeConditions = {
  'String': [function(argValue) { return true; }, 'String'],
  'Boolean': [function(argValue) { return true; }, 'Boolean'],
  'Int': [function(argValue) { return !isNaN(argValue); }, 'Number'],
  '+Int': [function(argValue) { return (!isNaN(argValue) && argValue * 1 >= 0); }, 'Number'] // represents + integers.
};

argTypeEnum  = {
  'String': 0,
  'Boolean': 1,
  'Number': 2
};

function argTypeCaster(argType, argValue) {
  switch (argTypeEnum[argType]) {
    case 0:
      return argValue;
    case 1:
      return true;
    case 2:
      return Number(argValue);
  }
}

function argBuilder(argObj) {
  if (argObj.key === null) {
    console.log(`Error: Key of argument '${arg}' cannot be null`);
    process.exit(1);
  }
  if (!(argObj.type in argTypeConditions)) {
    console.log(`Error: Invalid type of argument '${arg}'`);
    process.exit(1);
  }
  argList.push(argObj);
}

// argument validator function. Add additional validations here.

function parsedObjValidator(tempObj) {

  for (i = 0; i < argList.length; i++) {
    if (argList[i].isRequired === true && !(argList[i].key in tempObj)) {
      return new Error(`Value of '${argList[i].arg}'  required`);
    }
  }

  if (tempObj.remote === true && tempObj.local === true) {
    return new Error(`Remote and Local arguments cannot be true at the same time`);
  }
  return true;
}

function printParsedArgs(parsedObj) {
  console.log(parsedObj);
}

function argParser(inputArgs) {
  var  ii, jj, argValue, arg, tempObj = {};
  outerLoop:
    for (ii = 0; ii < inputArgs.length; ii++) {
      arg = inputArgs[ii];
      if (arg.indexOf('-') !== 0) {
        for (jj = 0; jj < argList.length; jj++) {
          if (argList[jj].position === ii) {
            tempObj[argList[jj].key] = arg;
            continue outerLoop;
          }
        }
      } else {
          arg = arg.split('=');
          for (jj = 0; jj < argList.length; jj++) {
            if (argList[jj].arg === arg[0]) {
              flag = 1;
              argValue = arg[1];
              if ( argTypeConditions[argList[jj].type][0](argValue)) {
                argValue = argTypeCaster(argTypeConditions[argList[jj].type][1], argValue);
                tempObj[argList[jj].key] = argValue;
                continue outerLoop;
              }
            }
          }
        }
        return new Error(`Invalid argument '${inputArgs[ii]}' entered. Check Type and Key`)
    }
   var validationResult = parsedObjValidator(tempObj);
   if (validationResult instanceof Error) {
     return validationResult;
   }
  return tempObj;
}

// add new arguments here in the format argBuilder({key: 'argKey', arg: argName, type: 'argType', isRequired: true/false, position: index});

argBuilder({ key: 'command', arg: null, type: 'String', isRequired: false, position: 0 });
argBuilder({ key: 'subcommand', arg: null, type: 'String', isRequired: false, position: 1 });
argBuilder({ key: 'key', arg: '--key', type: '+Int', isRequired: true, position: null });
argBuilder({ key: 'name', arg: '--name', type: 'String', isRequired: false, position: null });
argBuilder({ key: 'verbrose', arg: '-v', type: 'Boolean', isRequired: false, position: null });
argBuilder({ key: 'local', arg: '--local', type: 'Boolean', isRequired: false, position: null });
argBuilder({ key: 'remote', arg: '--remote', type: 'Boolean', isRequired: false, position: null });

var inputArgs = process.argv.slice(2);

var parsedObj = argParser(inputArgs);

if (parsedObj instanceof Error) {
  console.log(parsedObj);
  process.exit(1);
}
else
  printParsedArgs(parsedObj);
