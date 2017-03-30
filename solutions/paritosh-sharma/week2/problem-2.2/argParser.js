// jshint esversion: 6

var groupList = [];
var argTypeConditions = {};
var argTypeCaster  = {};
var argDataType = {};
var inputArgs = process.argv.slice(2);

module.exports = {};

module.exports.addArgType = function (argTypeObj) {
  argTypeConditions[argTypeObj.name] = argTypeObj.condition;
  argDataType[argTypeObj.name] = argTypeObj.dataType;
  argTypeCaster[argTypeObj.dataType] = argTypeObj.castFunction;
};


module.exports.addArgGroup = function (argObj) {
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
};

module.exports.addArg = function(argObj) {
  if(argObj.key === null) {
    throw new Error(`Key of argument '${argObj.arg}' cannot be null`);
  }
  if (!(argObj.type in argTypeConditions)) {
    throw new Error(`Invalid type of argument '${argObj.arg}'`);
  }
  var argGroupObj = { isRequired: argObj.isRequired || false, argList: [ { key: argObj.key, arg: argObj.arg, type: argObj.type, position: argObj.position || null } ] };
  groupList.push(argGroupObj);
};

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

function argParser() {
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

module.exports.parse = function() {
  try{
    return argParser();
  }
  catch(error) {
    console.log(error);
    process.exit(1);
  }
};
