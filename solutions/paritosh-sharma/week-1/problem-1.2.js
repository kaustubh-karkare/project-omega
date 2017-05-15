//jshint esversion: 6, node: true

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
    addGroupArg(argObj) {
      addArg(argObj, this);
    },
  };

  groupList.push(newGroupObj);
  return newGroupObj;
}

// common function to add individual arguments and arguments in groups.
function addArg(argObj, groupObj) {
  if (argObj.argName === null) {
    throw new Error(`argName of argument '${ argObj.argKey }' cannot be null`);
  }

  if (!(argObj.type in argTypeFunctions)) {
    throw new Error(`Invalid type of argument '${ argObj.argKey }'`);
  }

  if (groupObj) {
    let groupValid = false;
    groupValid = groupList.some(argGroup => {
      if (argGroup.name === groupObj.name) {
        argGroup.argList.push(argObj);
        return true;
      }
    });

    if (!groupValid) {
      throw new Error(`Group not found. Use a valid group object`);
    }
  } else {
    let argGroupObj = {
      isRequired: argObj.isRequired || false,
      argList: [argObj],
    };

    groupList.push(argGroupObj);
  }
}

/**
* argument validator function.
* add additional validations here.
*/
function parsedObjValidator(parseObj) {
  groupList.forEach(argGroup => {
    let count = 0;

    argGroup.argList.forEach(arg => {
      if (arg.argName in parseObj) {
        count += 1;
      }
    });
    if (argGroup.isRequired === true) {
      if (count === 0) {
        if (argGroup.argList.length === 1) {
          throw new Error(`Argument '${argGroup.argList[0].argKey}' required`);
        } else {
          throw new Error(`At least one argument from group '${ argGroup.name }' required.`);
        }
      }
    }

    if (count > 1) {
      throw new Error(`Multiple arguments of group '${ argGroup.name }' present.`);
    }
  });

  return true;
}

// main argument parser function
function parseArg(inputArgs) {
  const parseObj = {};

  inputArgs.forEach((inputArg, index) => {
    let argParsed = false;
    let argValue = null;
    let keyLessArg;
    const inputKey = inputArg.split('=')[0];
    const inputValue = inputArg.split('=')[1];

    if (inputKey.indexOf('-') !== 0) {
      keyLessArg = true;
    } else {
      keyLessArg = false;
    }

    argParsed = groupList.some(argGroup => {
      return argGroup.argList.some(arg => {
        if (keyLessArg) {
          if (arg.position === index) {
            argValue = argTypeFunctions[arg.type](inputKey);
          }
        } else {
          if (arg.argKey === inputKey) {
            argValue = argTypeFunctions[arg.type](inputValue);
          }
        }
        if (argValue !== null) {
          parseObj[arg.argName] = argValue;
          return true;
        }
      });
    });

    if (!argParsed) {
      throw new Error(`Invalid argument '${ inputKey }' entered. Check Type and argName`);
    }
  });

  parsedObjValidator(parseObj);
  return parseObj;
}

function intTypeFunction(argValue) {
  if (!isNaN(argValue)) {
    return Number(argValue);
  } else return null;
}

function pIntTypeFunction(argValue) {
  if ((!isNaN(argValue) && argValue * 1 >= 0)) {
    return Number(argValue);
  } else return null;
}

addArgType({ name: 'String', typeFunction: function(argValue) { return argValue; }, dataType: 'String', });
addArgType({ name: 'Boolean', typeFunction: function(argValue) { return true; }, dataType: 'Boolean', });
addArgType({ name: 'Int', typeFunction: intTypeFunction, dataType: 'Number', });
addArgType({ name: '+Int', typeFunction: pIntTypeFunction, dataType: 'Number', });

addArg({ argName: 'command', argKey: null, type: 'String', position: 0, });
addArg({ argName: 'subcommand', argKey: null, type: 'String', position: 1, });
addArg({ isRequired: true, argName: 'key', argKey: '--key', type: '+Int', });
addArg({ argName: 'name', argKey: '--name', type: 'String', });
addArg({ argName: 'verbrose', argKey: '-v', type: 'Boolean', });
const group1 = createGroup('group1');
group1.addGroupArg({ argName: 'local', argKey: '--local', type: 'Boolean', });
group1.addGroupArg({ argName: 'remote', argKey: '--remote', type: 'Boolean', });

const inputArgs = process.argv.slice(2);

try {
  let parsedObj = parseArg(inputArgs);
  console.log(parsedObj);
} catch(error) {
  console.log(error);
}
