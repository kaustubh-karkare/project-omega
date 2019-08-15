/**
 * Exception Class
 * @param {string} message
 */
function InvalidArgumentException(message) {
  this.message = message;
}
/**
 * Exception Class
 * @param {string} message
 */
function InvalidArgumentTypeException(message) {
  this.message = message;
}
/**
 * Exception Class
 * @param {string} message
 */
function MalformedArgumentException(message) {
  this.message = message;
}
/**
 * Exception Class
 * @param {string} message
 */
function MissingRequiredArgumentException(message) {
  this.message = message;
}

module.exports = class Parser {
  /**
   * @constructor
   */
  constructor() {
    // Stores serialized arguments
    this.jsonArgs = undefined;

    // Stores argument data with indexed key starting from 1 (index : {Data})
    this.indexedArgs = {};

    // Stores Indexes for each argument (argName: index)
    this.argIndices = {};

    // Used to keep track of new arguments
    this.indexOfNewArg = 1;
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
   * Valid Types: 'string', 'positive-integer', 'boolean
   * @param {string} smallArg
   * @param {sring} largeArg
   * @param {string} description
   * @param {type} defaultValue
   * @param {string} type
   * @param {boolean} isRequired
   * @return {this}
   */
  option(smallArg, largeArg, description,
      defaultValue, type = 'string', isRequired = false) {
    smallArg = smallArg.replace('-', ''); // single character version of arg
    largeArg = largeArg.replace('--', ''); // multi-character version of arg

    this.indexedArgs[this.indexOfNewArg] = {
      smallArg: smallArg,
      largeArg: largeArg,
      value: defaultValue,
      description: description,
      type: type,
      isRequired: isRequired,
    };

    // Set the validator function, which checks if value is of correct type
    switch (type) {
      case 'positive-integer': {
        this.indexedArgs[this.indexOfNewArg].validator = this.isPositiveNumber;
        break;
      }
      case 'string': {
        this.indexedArgs[this.indexOfNewArg].validator = (arg) => {
          return true;
        };
        break;
      }
      case 'boolean': {
        this.indexedArgs[this.indexOfNewArg].validator = (arg) => {
          return typeof (arg) === 'boolean';
        };
        break;
      }
    }

    // Store in argIndices
    this.argIndices[smallArg] = this.indexOfNewArg.toString();
    this.argIndices[largeArg] = this.indexOfNewArg.toString();
    ++this.indexOfNewArg;

    return this;
  }

  /**
   * Populates arg values and checks for syntactic and type correctness
   * @param {object} argList
   * @return {this}
   */
  parse(argList) {
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
          const index = this.argIndices[smallArg];
          if (index === undefined) {
            throw new InvalidArgumentException(
                'Error: "' + arg + '" is not a valid argument');
          }
          if (!this.indexedArgs[index]['validator'](value)) {
            throw new InvalidArgumentTypeException(
                'Error: The value for the "-' + smallArg.toString() +
                '" argument must be a ' + this.indexedArgs[index]['type'] +
                '.');
          }
          this.indexedArgs[index]['value'] = value;
        });
      } else if (this.isLargeArg(arg)) {
        // Large version of arg passed
        const largeArg = arg.replace('--', '');
        const index = this.argIndices[largeArg];
        if (index === undefined) {
          throw new InvalidArgumentException(
              'Error: "' + arg + '" is not a valid argument');
        }
        if (!this.indexedArgs[index]['validator'](value)) {
          throw new InvalidArgumentTypeException(
              'Error: The value for the "-' + largeArg.toString() +
              '" argument must be a ' + this.indexedArgs[index]['type'] +
              '.');
        }
        this.indexedArgs[index]['value'] = value;
      } else {
        // Malformed Argument
        throw new MalformedArgumentException(
            'Error: Malformed argument ' + arg);
      }
    });
    return this;
  }

  /**
   * Serializes/Stores argList and returns it
   * @return {object} Serialized Argument List
   */
  opts() {
    if (this.jsonArgs === undefined) {
      const json = {};
      Object.keys(this.indexedArgs).forEach((key, index) => {
        const arg = this.indexedArgs[key];
        if (arg.isRequired && arg.value === undefined) {
          // Check if required=True arg has been set
          throw new MissingRequiredArgumentException(
              'Error: The \'--' + arg.largeArg +
              '\' argument is required, but missing from input.');
        }
        json[arg.largeArg] = arg.value;
      });
      this.jsonArgs = json;
    }
    return this.jsonArgs;
  }
};

const Parser = require('./parser');

const parser = new Parser();
parser
    .option('-k', '--key', 'key value, must be + integer'
        , undefined, 'positive-integer', true)
    .option('-n', '--name', '', undefined, 'string', false)
    .option('-l', '--local', '', undefined, 'boolean', false)
    .option('-r', '--remote', '', undefined, 'boolean', false);

try {
  parser.parse(process.argv);
  if (parser.opts().local && parser.opts().remote) {
    console.log(
        'Error:The "--local" and "--remote" arguments cannot be used together');
  } else {
    console.log(parser.opts());
  }
} catch (e) {
  console.log(e.message);
}
