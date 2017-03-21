// jshint esversion: 6

var groupList = [];
var argTypeConditions = {};
var argTypeCaster  = {};
var argDataType = {};

function addArgType(argTypeObj) {
  argTypeConditions[argTypeObj.name] = argTypeObj.condition;
  argDataType[argTypeObj.name] = argTypeObj.dataType;
  argTypeCaster[argTypeObj.dataType] = argTypeObj.castFunction;
}


function argGroupBuilder(argObj) {
  var ii;
  for(ii = 0; ii < argObj.argList.length; ii++) {
    if (argObj.argList[ii].key === null) {
      throw new Error(`Key of argument '${argObj.argList[ii].arg}' cannot be null`);
    }
    if (!(argObj.argList[ii].type in argTypeConditions)) {
      throw new Error(`Invalid type of argument '${argObj.argList[ii].arg}'`);
    }
  }
  groupList.push(argObj);
}

// argument validator function. Add additional validations here.

function parsedObjValidator(parseObj) {
  var ii, jj, count;
  for (ii = 0; ii < groupList.length; ii++) {
    count = 0;
    for (jj = 0; jj < groupList[ii].argList.length;  jj++) {
      if (groupList[ii].argList[jj].key in parseObj) {
        ++count;
      }
    }
    if (groupList[ii].isRequired === true) {
      if (count === 0) {
        throw new Error(`At least one argument from group of argument '${groupList[ii].argList[0].arg}' required.`);
      }
    }
    if (count > 1) {
      throw new Error(`Multiple arguments of group same as argument '${groupList[ii].argList[0].arg}' present.`);
    }
  }
return true;
}

function argParser(inputArgs) {
  var ii, jj, kk, argValue, arg, parseObj = {};
  outerLoop:
    for (ii = 0; ii < inputArgs.length; ii++) {
      arg = inputArgs[ii];
      if (arg.indexOf('-') !== 0) {
        for (jj = 0; jj < groupList.length; jj++) {
          for (kk = 0; kk < groupList[jj].argList.length; kk++) {
            if (groupList[jj].argList[kk].position === ii) {
              parseObj[groupList[jj].argList[kk].key] = arg;
              continue outerLoop;
            }
          }
        }
      } else {
        arg = arg.split('=');
        for (jj = 0; jj < groupList.length; jj++) {
          for (kk = 0; kk < groupList[jj].argList.length; kk++) {
            if (groupList[jj].argList[kk].arg === arg[0]) {
              argValue = arg[1];
              if ( argTypeConditions[groupList[jj].argList[kk].type](argValue)) {
                argValue = argTypeCaster[argDataType[groupList[jj].argList[kk].type]](argValue);
                parseObj[groupList[jj].argList[kk].key] = argValue;
                continue outerLoop;
              }
            }
          }
        }
      }
      throw new Error(`Invalid argument '${inputArgs[ii]}' entered. Check Type and Key`);
    }
  var validationResult = parsedObjValidator(parseObj);
  return parseObj;
}

// add new arg types here

addArgType({ name: 'String', condition: function(argValue) { return true; }, dataType: 'String', castFunction: function(argValue) { return argValue; } });
addArgType({ name: 'Boolean', condition: function(argValue) { return true; }, dataType: 'Boolean', castFunction: function(argValue) { return true; } });
addArgType({ name: 'Int', condition: function(argValue) { return !isNaN(argValue); }, dataType: 'Number', castFunction: function(argValue) { return Number(argValue); } });
addArgType({ name: '+Int', condition: function(argValue) { return (!isNaN(argValue) && argValue * 1 >= 0); }, dataType: 'Number', castFunction: function(argValue) { return Number(argValue); } });

// add new arguments here in the format argBuilder({key: 'argKey', arg: argName, type: 'argType', isRequired: true/false, position: index});

argGroupBuilder({ groupId: 1, isRequired: false, argList: [ { key: 'command', arg: null, type: 'String', position: 0 } ] });
argGroupBuilder({ groupId: 2, isRequired: false, argList: [ { key: 'subcommand', arg: null, type: 'String', position: 1 } ] });
argGroupBuilder({ groupId: 3, isRequired: true, argList: [ { key: 'key', arg: '--key', type: '+Int', position: null } ] });
argGroupBuilder({ groupId: 4, isRequired: false, argList: [ { key: 'name', arg: '--name', type: 'String', position: null } ] });
argGroupBuilder({ groupId: 5, isRequired: false, argList: [ { key: 'verbrose', arg: '-v', type: 'Boolean', position: null } ] });
argGroupBuilder({ groupId: 6, isRequired: false, argList: [ { key: 'local', arg: '--local', type: 'Boolean', position: null }, { key: 'remote', arg: '--remote', type: 'Boolean', position: null } ] });

var inputArgs = process.argv.slice(2);
try {
  var parsedObj = argParser(inputArgs);
  console.log(parsedObj);
} catch(error) {
  console.log(error);
}
