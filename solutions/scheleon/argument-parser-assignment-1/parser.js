/**
 * { 
 *   'Author' : 'Shubham Kumar',
 *   'Handle' : scheleon
 * }
 */

/**
 * Capitalize first letter of string
 * @param {String} string 
 */
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

class InvalidArgument extends Error {
    constructor(argumentLabel) {
        super(argumentLabel);
        this.name = "Invalid Argument";
    }
}

class WrongArgumentTypeException extends Error {
    constructor(property, expected, found) {
        super(property + " type expected : " + expected + ", found : " + found);
        this.name = this.constructor.name;
    }
}

class EmptyArgumentValueException extends Error {
    constructor(label) {
        super("Argument " + label + " cannot be empty");
        this.name = this.constructor.name;
    }
}

class Argument{
    /**
     * @constructor
     * @param {String} shortLabel 
     * @param {String} largeLabel 
     * @param {Boolean} isValueRequired 
     * @param {*} valueType 
     * @param {*} defaultValue 
     */
    constructor (shortLabel, largeLabel, isValueRequired, valueType, defaultValue) {
        this.shortLabel = shortLabel;
        this.largeLabel = largeLabel;
        this.isValueRequired = isValueRequired;
        this.valueType = valueType;
        
        var defaultValueType = typeof defaultValue;
        if (valueType != capitalizeFirstLetter(defaultValueType)) { //
            throw new WrongArgumentTypeException("Default Value", this.valueType, typeof defaultValue);
        } else {
            this.defaultValue = defaultValue;
        }
    }

    /**
     * Getters & Setters
     */
    getShortLabel() {
        return this.shortLabel;
    }

    getLargeLabel() {
        return this.largeLabel;
    }

    getIsValueRequired() {
        return this.isValueRequired;
    }

    getValueType() {
        return this.valueType;
    }

    getDefaultValue() {
        return this.defaultValue;
    }

    getValue() {
        return this.value;
    }
}

/**
 * Parser is the class containing an array of Argument class
 * reuired to be  passed by the users, and boolean flags.
 * This is the class to be exported using module.exports().
 */
class Parser {

    /**
     * Initiate argument array and argumentJson hashmap
     */
    constructor() {
        this.arguments = new Array();
        this.argumentJson = {};
        this.argumentIndexByLabel = {};
    }

    /**
    * Check if ans Argument with same label exists in the list else add an entry in the list
    * @param {String} shortLabel 
    * @param {String} largeLabel 
    * @param {Boolean} isValueRequired 
    * @param {*} valueType 
    * @param {*} defaultValue 
    */
    addArgument(shortLabel, largeLabel, isValueRequired, valueType, defaultValue) {
        
        if(shortLabel in this.argumentIndexByLabel || largeLabel in this.argumentIndexByLabel) {
            throw new InvalidArgument("Argument with the same label already exists");
        }

        var index = this.arguments.length;
        this.arguments[index] = new Argument(shortLabel, 
                                             largeLabel, 
                                             isValueRequired, 
                                             valueType, 
                                             defaultValue);
        this.argumentIndexByLabel[largeLabel] = Number(index);
        this.argumentIndexByLabel[shortLabel] = Number(index);
    }

    /**
     * Set the argument value from the list if it matches 
     * any argument's shortLabel or largeLabel in the hashmap  
     * @param {String} label 
     * @param {String} value 
     */
    setValue(label, value) {
        
        if (!(label in this.argumentIndexByLabel)) {
            throw new InvalidArgument(label + " not defined");
        }

        var index = Number(this.argumentIndexByLabel[label]);
        var valueTypeExpected = this.arguments[index].getValueType();
        var foundValueType = typeof value;

        if (valueTypeExpected == "String") { //
            try { //
                value = String(value);
                this.argumentJson[this.arguments[index].getLargeLabel()] = value;
            } catch (err) {
                throw new WrongArgumentTypeException("Value", valueTypeExpected, 
                    capitalizeFirstLetter(foundValueType));
            }
        } else if (valueTypeExpected == "Number") {
            
            try { //
                value = Number(value);
                if (isNaN(value)) {
                    throw new WrongArgumentTypeException("Value", valueTypeExpected, 
                        capitalizeFirstLetter(foundValueType));
                }
                this.argumentJson[this.arguments[index].getLargeLabel()] = value;
            } catch (err) {
                throw new WrongArgumentTypeException("Value", valueTypeExpected, 
                    capitalizeFirstLetter(foundValueType));
            }
        } else {
            try { //
                if (value == 'true') {
                    value = true;
                } else if (value == 'false') {
                    value = false;
                } else {
                    throw new WrongArgumentTypeException(this.arguments[index].getLargeLabel(),
                                                        this.arguments[index].getValueType(),
                                                        capitalizeFirstLetter(foundValueType));
                }
                this.argumentJson[this.arguments[index].getLargeLabel()] = value;
            } catch (err) {
                throw new WrongArgumentTypeException(this.arguments[index].getLargeLabel(), 
                                                    valueTypeExpected, 
                                                    capitalizeFirstLetter(foundValueType));
            }
        }
    } 

    /**
     * Returns index of argument label from the list if it matches 
     * any argument's shortLabel or largeLabel   
     * @param {String} label 
     */
    findArgumentIndexByLabel(label) {
        if(label in this.argumentIndexByLabel) {
            return this.argumentIndexByLabel[label];
        }
        throw new InvalidArgument(label);
    }

    listArgsProvided(providedArgumentList) {
        /**
        * For Argument type : -key
        */
        var shortArgv = "^-[\\w]+$";
        /**
        * For Argument type : --key
        */
        var largeArgv = "^--[\\w]+$";
        /**
        * For Argument type : -key=value
        */
        var shortInputArgv = "^-[\\w]+=[\\w ]+$"
        /**
         * For Argument type : --key=value
         */
        var largeInputArgv = "^--[\\w]+=[\\w ]+$";
        /**
         * Reuired if argument is of type : -key value
         */
        var inputValue = "^[\\w ]+$";

        for(var ii = 2; ii < providedArgumentList.length; ii++) {    
            if(providedArgumentList[ii].match(shortArgv) != null 
                || providedArgumentList[ii].match(largeArgv) != null) { //

                var label = providedArgumentList[ii].match("[\\w]+")[0];
                var argumentIndex = this.findArgumentIndexByLabel(label);
                
                /**
                 * Set { "value" : true }, if isValueRequired == false, else
                 * increase the iterator and perform a check for value on next argument 
                 */
                if (this.arguments[argumentIndex].getIsValueRequired() == true) { //
                    ii++;

                    /**
                     * Check if the iterator reaches the end of the passed arguments array
                     */
                    if(ii == providedArgumentList.length) {
                        throw new EmptyArgumentValueException(label);
                    }
                    var argvValueProvided = providedArgumentList[ii].match(inputValue);
                    if(argvValueProvided != null) {
                        this.setValue(label, argvValueProvided);
                    } else {
                        throw new EmptyArgumentValueException(label);
                    }
                } else {

                    /**
                     * if isValueRequired == false, then provided argv is a flag, set true
                     */
                    this.setValue(label, true);
                } 
            } else if (providedArgumentList[ii].match(shortInputArgv) != null 
                || providedArgumentList[ii].match(largeInputArgv) != null) {
                
                /**
                 * Extract the Argument Label
                 */
                var label = providedArgumentList[ii].match("[\\w]+=")[0];
                label = label.substring(0 , label.length - 1);    
                
                /**
                * Extract the value from argument
                */
                var value = providedArgumentList[ii].match("=[\\w -]+")[0];
                argvValueProvided = value.substring(1 , value.length);

                /**
                 * Calls the setValue function which further calls Argument.setValue() 
                 */
                this.setValue(label, argvValueProvided);
            } else {
                throw new InvalidArgument(providedArgumentList[ii]);
            }
        }
    }
    
    /**
     * Returns populated argumentJson string
     * Key -> label
     * Value -> value
     */
}

module.exports = new Parser;