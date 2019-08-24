function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

class Argument{
    constructor (shortLabel, largeLabel, isValueRequired, valueType, defaultValue) {
        this.shortLabel = shortLabel;
        this.largeLabel = largeLabel;
        this.isValueRequired = isValueRequired;
        this.valueType = valueType;
        
        var defaultValueType = typeof defaultValue;
        if (valueType != capitalizeFirstLetter(defaultValueType)) {
            throw "Default value not of type " + valueType;
        } else {
            this.defaultValue = defaultValue;
            this.value = defaultValue;
        }
    }

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

    setValue(value){
        var valueType = typeof value;
        valueType = capitalizeFirstLetter(valueType)
        
        if (this.valueType == "Number" && this.valueType == valueType) {
            this.value = Number(value);
        } else if (this.valueType == "String" && this.valueType == valueType) {
            this.value = String(value);
        } else if(this.valueType == "Boolean" && this.valueType == valueType) {
            this.value = Boolean(value);
        } else {
            throw "Expected : " + this.valueType + ", but got " + valueType;
        }
    }
}

class Parser {
    constructor() {
        this.arguments = new Array();
        this.argumentJson = {};
    }

    addArgument(shortLabel, largeLabel, isValueRequired, valueType, defaultValue) {
        for (var i = 0; i < this.arguments.length; i++) {
            if(shortLabel == this.arguments[i].getShortLabel() || largeLabel == this.arguments[i].getLargeLabel()) {
                throw "Argument with the same label already exists";
                return;
            }
        }
        var index = this.arguments.length;
        this.arguments[index] = new Argument(shortLabel, largeLabel, isValueRequired, valueType, defaultValue);
    }

    setValue(label, value) {
        for (var i = 0; i < this.arguments.length; i++) {
            if(label == this.arguments[i].getShortLabel() || label == this.arguments[i].getLargeLabel()) {
                return this.arguments[i].setValue(value);
            }
        }
        throw "Argument not found!";
    } 

    findArgumentIndexByLabel(label) {
        for (var i = 0; i < this.arguments.length; i++) {
            if(label == this.arguments[i].getShortLabel() || label == this.arguments[i].getLargeLabel()) {
                return i;
            }
        }
        throw label + " : undefined argument";
    }

    listArgsProvided() {
        var shortArgv = "^-[\\w]+$";
        var largeArgv = "^--[\\w]+$";
        var shortInputArgv = "^-[\\w]+=[\\w ]+$"
        var largeInputArgv = "^--[\\w]+=[\\w ]+$";
        /**
         * Reuired if argument is of type : -key value
         */
        var inputValue = "^[\\w -]+$";

        for(var itr=2; itr < process.argv.length; itr++) {    
            if(process.argv[itr].match(shortArgv) != null || process.argv[itr].match(largeArgv) != null) {

                var label = process.argv[itr].match("[\\w]+")[0];
                var argumentIndex = this.findArgumentIndexByLabel(label);
                
                /**
                 * Set { "value" : true }, if isValueRequired == false
                 */
                if (this.arguments[argumentIndex].getIsValueRequired() == true) {
                    itr++;
                    var argvValueProvided = process.argv[itr].match(inputValue);
                    if(argvValueProvided != null) {
                        this.arguments[argumentIndex].setValue(argvValueProvided);
                    } else {
                        throw "Argument " + label + " cannot be empty";
                    }
                } else {
                    this.arguments[argumentIndex].setValue(true);
                } 
            } else if (process.argv[itr].match(shortInputArgv) != null || process.argv[itr].match(largeInputArgv) != null) {
                var label = process.argv[itr].match("[\\w]+=")[0];
                label = label.substring(0 , label.length - 1);    
                
                var value = process.argv[itr].match("=[\\w -]+")[0];
                argvValueProvided = value.substring(1 , value.length); 
                this.setValue(label, argvValueProvided);
            } else {
                throw "Wrong argument" + process.argv[itr];
            }
        }
        this.setAllArgs();   
    }

    setAllArgs() {
        for (var itr = 0; itr < this.arguments.length; itr++) {
            this.argumentJson[this.arguments[itr].getLargeLabel()] = this.arguments[itr].getValue();
        }
    }
}

module.exports = new Parser;