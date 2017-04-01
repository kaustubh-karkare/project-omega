// jshint esversion: 6, node: true

"use strict";

const groupList = [];
const argTypeFunctions = {};
const argDataType = {};
const inputArgs = process.argv.slice(2);

module.exports = {};

module.exports.addArgType =  function(argTypeObj) {
  argTypeFunctions[argTypeObj.name] = argTypeObj.typeFunction;
  argDataType[argTypeObj.name] = argTypeObj.dataType;
};

module.exports.createGroup = function(groupName) {
  if (!groupName) {
    throw new Error(`Group name required while creating new group`);
  }
  let newGroupObj = {
    name: groupName,
    isRequired: false,
    argList: [],
    addGroupArg: function(argObj) {
      if (argObj.key === null) {
        throw new Error(`Key of argument '${argObj.arg}' cannot be null`);
      }
      if (!(argObj.type in argTypeFunctions)) {
        throw new Error(`Invalid type of argument '${argObj.arg}'`);
      }
      for (let ii = 0; ii < groupList.length; ii++) {
        if (groupList[ii].name === this.name) {
          groupList[ii].argList.push(argObj);
        }
      }
    }
  };
  groupList.push(newGroupObj);
  return newGroupObj;
};

module.exports.addArg = function(argObj) {
  if (argObj.key === null) {
    throw new Error(`Key of argument '${argObj.arg}' cannot be null`);
  }
  if (!(argObj.type in argTypeFunctions)) {
    throw new Error(`Invalid type of argument '${argObj.arg}'`);
  }
  let argGroupObj = { isRequired: argObj.isRequired || false, argList: [ { key: argObj.key, arg: argObj.arg, type: argObj.type, position: argObj.position } ] };
  groupList.push(argGroupObj);
};

// argument validator function. Add additional validations here.

function parsedObjValidator(parseObj) {
  let ii, jj, count;
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

function parseArg(){
  let ii, jj, kk, argValue, arg, parseObj = {};
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
              argValue = argTypeFunctions[groupList[jj].argList[kk].type](argValue);
              if (argValue) {
                parseObj[groupList[jj].argList[kk].key] = argValue;
                continue outerLoop;
              }
            }
          }
        }
      }
      throw new Error(`Invalid argument '${inputArgs[ii]}' entered. Check Type and Key`);
    }
  let validationResult = parsedObjValidator(parseObj);
  return parseObj;
}

module.exports.parse = function() {
  try{
    return parseArg();
  }
  catch(error) {
    console.log(error);
    process.exit(1);
  }
};
