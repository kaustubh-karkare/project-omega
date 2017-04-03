// jshint esversion: 6, node: true

"use strict";

const groupList = [];
const argTypeFunctions = {};
const argDataType = {};

function addArgType(argTypeObj) {
  argTypeFunctions[argTypeObj.name] = argTypeObj.typeFunction;
  argDataType[argTypeObj.name] = argTypeObj.dataType;
}

// function to create groups

function createGroup(groupName) {
  if (!groupName) {
    throw new Error(`Group name required while creating new group`);
  }
  const newGroupObj = {
    name: groupName,
    isRequired: false,
    argList: [],
    addGroupArg: function(argObj) {
      addArg(argObj, this);
    }
  };
  groupList.push(newGroupObj);
  return newGroupObj;
}

//common function to add individual arguments and arguments in groups.

function addArg(argObj, groupObj) {
  if (argObj.argName === null) {
    throw new Error(`argName of argument '${argObj.arg}' cannot be null`);
  }
  if (!(argObj.type in argTypeFunctions)) {
    throw new Error(`Invalid type of argument '${argObj.arg}'`);
  }
  if (groupObj) {
    for (let ii = groupList.length-1; ii >= 0; ii--) {
      if (groupList[ii].name === groupObj.name) {
        groupList[ii].argList.push(argObj);
      }
    }
  } else {
    let argGroupObj = { isRequired: argObj.isRequired || false, argList: [ { argName: argObj.argName, arg: argObj.arg, type: argObj.type, position: argObj.position } ] };
    groupList.push(argGroupObj);
  }
}

//argument validator function. Add additional validations here.

function parsedObjValidator(parseObj) {
  let ii, jj, count;
  for (ii = 0; ii < groupList.length; ii++) {
    count = 0;
    for (jj = 0; jj < groupList[ii].argList.length;  jj++) {
      if (groupList[ii].argList[jj].argName in parseObj) {
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

//main arggument parser funciton

function parseArg(inputArgs) {
  let ii, jj, kk, argValue, inputArg, parseObj = {};
  outerLoop:
    for (ii = 0; ii < inputArgs.length; ii++) {
      inputArg = inputArgs[ii].split('=');
      if (inputArg[0].indexOf('-') !== 0) {
        for (jj = 0; jj < groupList.length; jj++) {
          for (kk = 0; kk < groupList[jj].argList.length; kk++) {
            if (groupList[jj].argList[kk].position === ii) {
              parseObj[groupList[jj].argList[kk].argName] = inputArg[0];
              continue outerLoop;
            }
          }
        }
      } else {
        for (jj = 0; jj < groupList.length; jj++) {
          for (kk = 0; kk < groupList[jj].argList.length; kk++) {
            if (groupList[jj].argList[kk].arg === inputArg[0]) {
              argValue = argTypeFunctions[groupList[jj].argList[kk].type](inputArg[1]);
              if (argValue !== null) {
                parseObj[groupList[jj].argList[kk].argName] = argValue;
                continue outerLoop;
              }
            }
          }
        }
      }
      throw new Error(`Invalid argument '${inputArgs[ii]}' entered. Check Type and argName`);
    }
  let validationResult = parsedObjValidator(parseObj);
  return parseObj;
}

function intTypeFunction(argValue) {
  if (!isNaN(argValue)) {
    return Number(argValue);
  } else {
    return null;
  }
}

function pIntTypeFunction(argValue) {
  if ((!isNaN(argValue) && argValue * 1 >= 0)) {
    return Number(argValue);
  } else {
    return null;
  }
}

addArgType({ name: 'String', typeFunction: function(argValue) { return argValue; }, dataType: 'String' });
addArgType({ name: 'Boolean', typeFunction: function(argValue) { return true; }, dataType: 'Boolean' });
addArgType({ name: 'Int', typeFunction: intTypeFunction, dataType: 'Number' });
addArgType({ name: '+Int', typeFunction: pIntTypeFunction, dataType: 'Number' });

addArg({ argName: 'command', arg: null, type: 'String', position: 0 });
addArg({ argName: 'subcommand', arg: null, type: 'String', position: 1 });
addArg({ isRequired: true, argName: 'key', arg: '--key', type: '+Int' });
addArg({ argName: 'name', arg: '--name', type: 'String' });
addArg({ argName: 'verbrose', arg: '-v', type: 'Boolean' });
const group1 = createGroup('group1');
group1.addGroupArg({ argName: 'local', arg: '--local', type: 'Boolean' });
group1.addGroupArg({ argName: 'remote', arg: '--remote', type: 'Boolean' });

const inputArgs = process.argv.slice(2);
try {
  let parsedObj = parseArg(inputArgs);
  console.log(parsedObj);
} catch(error) {
  console.log(error);
}
