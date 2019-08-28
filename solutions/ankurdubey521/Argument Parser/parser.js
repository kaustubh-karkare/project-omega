const NE = require('node-exceptions');

/**
 * Argument Definition Class
 */
class Argument {
  /**
   * @constructor
   * @param {string} smallArg
   * @param {string} largeArg
   * @param {type} defaultValue
   * @param {string} description
   * @param {string} type
   * @param {boolean} isRequired
   * @param {string} dest
   * @param {number} nargs
   */
  constructor(smallArg, largeArg, defaultValue,
      description, type, isRequired, dest, nargs) {
    this.smallArg = smallArg;
    this.largeArg = largeArg;
    this.defaultValue = defaultValue;
    this.description = description;
    this.type = type;
    this.isRequired = isRequired;
    this.dest = dest;
    this.nargs = nargs;
  }
};

module.exports = class Parser {
  /**
   * @constructor
   */
  constructor() {
    // Stores serialized arguments
    this.jsonArgs = undefined;

    // Stores argument description with indexed key starting from 1
    this.indexedArgs = {};

    // Stores Indexes for each argument (argName: index)
    this.argnameIndexMap = {};

    // Used to keep track of new arguments
    this.indexOfNewArg = 1;

    // List of mutually exclusive argument groups
    this.exclusiveGroups = [];

    // Enums for Argument Types
    this.type = {
      STRING: 'string',
      POSITIVE_INTEGER: 'positive-integer',
      BOOLEAN: 'boolean',
    };

    // Custom Exception Classes
    this.InvalidArgumentException = class extends NE.LogicalException {};
    this.InvalidArgumentTypeException = class extends NE.LogicalException {};
    this.InvalidNumberOfArgumentException =
      class extends NE.LogicalException {};
    this.MalformedArgumentException = class extends NE.LogicalException {};
    this.MissingRequiredArgumentException =
      class extends NE.LogicalException {};
    this.MutuallyExclusiveArgumentsPassedException =
      class extends NE.LogicalException {};
  }

  /**
   * Checks if arg is a small argument
   * @param {string} arg
   * @return {boolean}
   */
  isSmallArg(arg) {
    const regex = /^-\w+/i;
    return arg.match(regex);
  }
  /**
   * Checks if arg is a large argument
   * @param {string} arg
   * @return {boolean}
   */
  isLargeArg(arg) {
    const regex = /^--\w+/i;
    return arg.match(regex);
  }
  /**
   * Checks if arg is a number
   * @param {string} arg
   * @return {boolean}
   */
  isPositiveNumber(arg) {
    if (typeof (arg) === 'boolean') {
      return false;
    }
    const regex = /^\d+$/i;
    return arg.match(regex);
  }

  /**
   * Defines and arguments and it's options
   * Valid Types: 'string', 'positive-integer', 'boolean'
   * @param {string} smallArg
   * @param {sring} largeArg
   * @param {string} description
   * @param {type} defaultValue
   * @param {string} type
   * @param {boolean} isRequired
   * @return {this}
   */
  addOption({smallArg, largeArg, description = '', defaultValue = undefined,
    type = this.type.STRING, isRequired = false, nargs = 1, dest = undefined}) {
    smallArg = smallArg.replace('-', ''); // single character version of arg
    largeArg = largeArg.replace('--', ''); // multi-character version of arg

    // Set default dest to be largeArg name
    if (dest == undefined) {
      dest = largeArg;
    }

    // Set/Override nargs = 0 for boolean arguments
    if (type == this.type.BOOLEAN) {
      nargs = 0;
    }

    this.indexedArgs[this.indexOfNewArg] = new Argument(smallArg, largeArg,
        defaultValue, description, type, isRequired, dest, nargs);

    // Set the validator function, which checks if value is of correct type
    switch (type) {
      case this.type.POSITIVE_INTEGER: {
        this.indexedArgs[this.indexOfNewArg].validator = this.isPositiveNumber;
        break;
      }
      case this.type.STRING: {
        this.indexedArgs[this.indexOfNewArg].validator = (arg) => {
          return true;
        };
        break;
      }
      case this.type.BOOLEAN: {
        this.indexedArgs[this.indexOfNewArg].validator = (arg) => {
          return typeof (arg) === 'boolean';
        };
        break;
      }
    }

    // Store in argnameIndexMap
    this.argnameIndexMap[smallArg] = this.indexOfNewArg.toString();
    this.argnameIndexMap[largeArg] = this.indexOfNewArg.toString();
    ++this.indexOfNewArg;

    return this;
  }

  /**
   * Populates arg values and checks for syntactic and type correctness
   * @param {object} argList
   * @return {Object} args
   */
  parse(argList) {
    const argValues = {};

    // Scan arglist and break any strings having '='
    // into string and value.
    let temp = [];
    for (let i = 0; i < argList.length; ++i) {
      if (argList[i].indexOf('=') != -1) {
        let arg = '';
        let value = '';
        [arg, value] = argList[i].split('=');
        temp.push(arg);
        temp.push(value);
      } else {
        temp.push(argList[i]);
      }
    }
    argList = temp;

    // Scan arglist and break any string having multiple
    // single character args into individual args.
    temp = [];
    for (let i = 0; i < argList.length; ++i) {
      if (this.isSmallArg(argList[i])) {
        argList[i].replace('-', '').split('').forEach((smallArg) => {
          temp.push('-' + smallArg);
        });
      } else {
        temp.push(argList[i]);
      }
    }
    argList = temp;

    // Scan list from end. Push any values into a list.
    // If an argument is found, assign all values to that argument.
    // Check nargs and type of value
    let values = [];
    for (let i = argList.length - 1; i >= 0; --i) {
      const item = argList[i];
      if (this.isSmallArg(item) || this.isLargeArg(item)) {
        // Arg passed
        let arg = '';
        if (this.isSmallArg(item)) {
          arg = item.replace('-', '');
        } else {
          arg = item.replace('--', '');
        }

        const index = this.argnameIndexMap[arg];

        // Check if argument is valid
        if (index === undefined) {
          throw new this.InvalidArgumentException(
              'Error: "' + arg + '" is not a valid argument');
        }

        const config = this.indexedArgs[index];

        // Check if nargs is satisfied
        if (values.length != config.nargs) {
          throw new this.InvalidNumberOfArgumentException(
              'Error: Expected ' + config.nargs.toString() +
              ' but found ' + values.length.toString() + ' arguments'
          );
        }

        // Check value type validity
        values.forEach((value) => {
          if (!config.validator(value)) {
            throw new this.InvalidArgumentTypeException(
                'Error: The value for the "-' + item.toString() +
                '" argument must be a ' + config.type + '.');
          }
        });

        // Set values and reset value array.
        // In case boolean value is passed, set it to [true]
        if (config.type === this.type.BOOLEAN) {
          argValues[config.dest] = [true];
        } else {
          argValues[config.dest] = values;
        }
        values = [];
      } else {
        // Value passed
        values.push(item);
      }
    }

    // Set default values if not already set
    Object.keys(this.indexedArgs).forEach((key, index) => {
      const arg = this.indexedArgs[key];
      if (argValues[arg.dest] === undefined && arg.defaultValue != undefined) {
        argValues[arg.dest] = [arg.defaultValue];
      }
    });

    return argValues;
  }

  /**
   * Sets arguments passed to be mutually exclusive
   * @param {list} argList: list of argument names (large version only)
   */
  setMutuallyExclusive(argList) {
    this.exclusiveGroups.push(argList);
  }

  /**
   * Serializes/Stores argList and returns it
   * @param {list} argList
   * @return {object} Serialized Argument List
   */
  parseOpts(argList) {
    const argsValue = this.parse(argList);

    // Check for required arguments
    Object.keys(this.indexedArgs).forEach((key, index) => {
      const arg = this.indexedArgs[key];
      if (arg.isRequired && argsValue[arg['dest']] === undefined) {
        // Check if required=True arg has been set
        throw new this.MissingRequiredArgumentException(
            'Error: The \'--' + arg.largeArg +
            '\' argument is required, but missing from input.');
      }
    });

    // Check for mutually exclusive arguments
    this.exclusiveGroups.forEach((list) => {
      let setArgCount = 0;
      const setArgs = [];
      list.forEach((arg) => {
        const trimmedArg = arg.replace('--', '');
        if (argsValue[trimmedArg] != undefined) {
          ++setArgCount;
          setArgs.push(trimmedArg);
        }
      });
      if (setArgCount > 1) {
        throw new
        this.MutuallyExclusiveArgumentsPassedException(
            'Error: The arguments "'
           + setArgs.toString() + '" cannot be passed together.');
      }
    });

    return argsValue;
  }
};
