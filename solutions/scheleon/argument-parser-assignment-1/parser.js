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
            throw "Default value not of type " + valueType;
        } else {
            this.defaultValue = defaultValue;
            this.value = defaultValue;
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

    /**
     * Check for required value types from String, Number, Boolean
     * set value after type casting to {valueType}
     * @param {*} value 
     */
    setValue(value){
        if (this.valueType == "String") { //
            try { //
                this.value = String(value);
            } catch (err) {
                var valueType = typeof value;
                throw "Expected : " + this.valueType + ", found " 
                    + capitalizeFirstLetter(valueType);
            }
        } else if (this.valueType == "Number") {
            try { //
                this.value = Number(value);
                if (isNaN(this.value)) {
                    throw "Expected : " + this.valueType + ", found " 
                        + capitalizeFirstLetter(valueType);
                }
            } catch (err) {
                var valueType = typeof value;
                throw "Expected : " + this.valueType + ", found " 
                    + capitalizeFirstLetter(valueType);
            }
        } else {
            try { //
                this.value = Boolean(value);
            } catch (err) {
                var valueType = typeof value;
                throw "Expected : " + this.valueType + ", found " 
                    + capitalizeFirstLetter(valueType);
            }
        }
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
        for (var i = 0; i < this.arguments.length; i++) {
            if(shortLabel == this.arguments[i].getShortLabel() 
                || largeLabel == this.arguments[i].getLargeLabel()) {
                throw "Argument with the same label already exists";
                return;
            }
        }
        var index = this.arguments.length;
        this.arguments[index] = new Argument(shortLabel, 
                                             largeLabel, 
                                             isValueRequired, 
                                             valueType, 
                                             defaultValue);
    }

    /**
     * Set the argument value from the list if it matches 
     * any argument's shortLabel or largeLabel   
     * @param {String} label 
     * @param {String} value 
     */
    setValue(label, value) {
        for (var i = 0; i < this.arguments.length; i++) {
            if(label == this.arguments[i].getShortLabel() 
                || label == this.arguments[i].getLargeLabel()) { //
                return this.arguments[i].setValue(String(value));
            }
        }
        throw "Argument not found!";
    } 

    /**
     * Returns index of argument label from the list if it matches 
     * any argument's shortLabel or largeLabel   
     * @param {String} label 
     */
    findArgumentIndexByLabel(label) {
        for (var i = 0; i < this.arguments.length; i++) {
            if(label == this.arguments[i].getShortLabel() 
                || label == this.arguments[i].getLargeLabel()) { //
                return i;
            }
        }
        throw label + " : undefined argument";
    }

    listArgsProvided() {
        var shortArgv = "^-[\\w]+$";
        /**
        * For Argument type : --key
        */
        var largeArgv = "^--[\\w]+$";
        /**
        * For Argument type : --key
        */
        var shortInputArgv = "^-[\\w]+=[\\w ]+$"
        /**
         * For Argument type : -key=value
         */
        var largeInputArgv = "^--[\\w]+=[\\w ]+$";
        /**
         * Reuired if argument is of type : -key value
         */
        var inputValue = "^[\\w -]+$";

        for(var itr=2; itr < process.argv.length; itr++) {    
            if(process.argv[itr].match(shortArgv) != null 
                || process.argv[itr].match(largeArgv) != null) { //

                var label = process.argv[itr].match("[\\w]+")[0];
                var argumentIndex = this.findArgumentIndexByLabel(label);
                
                /**
                 * Set { "value" : true }, if isValueRequired == false, else
                 * increase the iterator and perform a check for value on next argument 
                 */
                if (this.arguments[argumentIndex].getIsValueRequired() == true) { //
                    itr++;

                    /**
                     * Check if the iterator reaches the end of the passed arguments array
                     */
                    if(itr == process.argv.length) {
                        throw "Argument " + label + " cannot be empty";
                    }
                    var argvValueProvided = process.argv[itr].match(inputValue);
                    if(argvValueProvided != null) {
                        this.arguments[argumentIndex].setValue(argvValueProvided);
                    } else {
                        throw "Argument " + label + " cannot be empty";
                    }
                } else {

                    /**
                     * if isValueRequired == false, then provided argv is a flag, set true
                     */
                    this.arguments[argumentIndex].setValue(true);
                } 
            } else if (process.argv[itr].match(shortInputArgv) != null 
                || process.argv[itr].match(largeInputArgv) != null) {
                /**
                 * Extract the Argument Label
                 */
                var label = process.argv[itr].match("[\\w]+=")[0];
                label = label.substring(0 , label.length - 1);    
                
                /**
                * Extract the value from argument
                */
                var value = process.argv[itr].match("=[\\w -]+")[0];
                argvValueProvided = value.substring(1 , value.length);

                /**
                 * Calls the setValue function which further calls Argument.setValue() 
                 */
                this.setValue(label, argvValueProvided);
            } else {
                throw "Wrong argument " + label;
            }
        }
        this.setAllArgs();   
    }
    
    /**
     * Returns populated argumentJson string
     * Key -> label
     * Value -> value
     */
    setAllArgs() {
        for (var itr = 0; itr < this.arguments.length; itr++) {
            this.argumentJson[this.arguments[itr].getLargeLabel()] 
                = this.arguments[itr].getValue();
        }
        return argumentJson.toString();
    }
}

module.exports = new Parser;