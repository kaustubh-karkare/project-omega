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
   */
  constructor(smallArg, largeArg, defaultValue, description, type, isRequired) {
    this.smallArg = smallArg;
    this.largeArg = largeArg;
    this.defaultValue = defaultValue;
    this.description = description;
    this.type = type;
    this.isRequired = isRequired;
  }
};

module.exports = class Parser {
  /**
   * Exception Class
   * @param {string} message
   */
  InvalidArgumentException(message) {
    this.message = message;
  }
  /**
   * Exception Class
   * @param {string} message
   */
  InvalidArgumentTypeException(message) {
    this.message = message;
  }
  /**
   * Exception Class
   * @param {string} message
   */
  MalformedArgumentException(message) {
    this.message = message;
  }
  /**
   * Exception Class
   * @param {string} message
   */
  MissingRequiredArgumentException(message) {
    this.message = message;
  }
  /**
   * Exception Class
   * @param {string} message
   */
  MutuallyExclusiveArgumentsPassedException(message) {
    this.message = message;
  }

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
  setOption({smallArg, largeArg, description = '',
    defaultValue = undefined, type = 'string', isRequired = false}) {
    smallArg = smallArg.replace('-', ''); // single character version of arg
    largeArg = largeArg.replace('--', ''); // multi-character version of arg

    this.indexedArgs[this.indexOfNewArg] = new Argument(smallArg, largeArg,
        defaultValue, description, type, isRequired);


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

    argList = argList.slice(2); // Remove node and executable name from list

    argList.forEach((arg) => {
      // Check if arg has a value explicitly defined
      // if yes extract it else interpret as a boolean true
      let value = '';
      if (arg.indexOf('=') != -1) {
        value = arg.slice(arg.indexOf('=') + 1);
        arg = arg.slice(0, arg.indexOf('='));
      } else {
        value = true;
      }

      if (this.isSmallArg(arg)) {
        // Small version of Arg passed
        arg.replace('-', '').split('').forEach((smallArg) => {
          const index = this.argnameIndexMap[smallArg];
          if (index === undefined) {
            throw new this.InvalidArgumentException(
                'Error: "' + arg + '" is not a valid argument');
          }
          if (!this.indexedArgs[index]['validator'](value)) {
            throw new this.InvalidArgumentTypeException(
                'Error: The value for the "-' + smallArg.toString() +
                '" argument must be a ' + this.indexedArgs[index]['type'] +
                '.');
          }
          argValues[this.indexedArgs[index]['largeArg']] = value;
        });
      } else if (this.isLargeArg(arg)) {
        // Large version of arg passed
        const largeArg = arg.replace('--', '');
        const index = this.argnameIndexMap[largeArg];
        if (index === undefined) {
          throw new this.InvalidArgumentException(
              'Error: "' + arg + '" is not a valid argument');
        }
        if (!this.indexedArgs[index]['validator'](value)) {
          throw new this.InvalidArgumentTypeException(
              'Error: The value for the "-' + largeArg.toString() +
              '" argument must be a ' + this.indexedArgs[index]['type'] +
              '.');
        }
        argValues[this.indexedArgs[index]['largeArg']] = value;
      } else {
        // Malformed Argument
        throw new this.MalformedArgumentException(
            'Error: Malformed argument ' + arg);
      }
    });

    Object.keys(this.indexedArgs).forEach((key, index) => {
      const arg = this.indexedArgs[key];
      if (argValues[arg.largeArg] === undefined) {
        argValues[arg.largeArg] = arg.defaultValue;
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
      if (arg.isRequired && argsValue[arg['largeArg']] === undefined) {
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
            + setArgs.toString() + '" cannot be passed together.'
        );
      }
    });

    return argsValue;
  }
};
