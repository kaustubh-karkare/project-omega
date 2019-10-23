
# Argument-Parser

## Adding accepted arguments

#### Import module from Parser
`const parser = require("./parser");`

#### Call parser.addArgument() method with mentioned parameters

```Parameters
* @param {String} shortLabel 
* @param {String} largeLabel 
* @param {Boolean} isValueRequired 
* @param {*} valueType 
* @param {*} defaultValue
```

`parser.addArgument("S", "sampleLargeArgument", true, "String", "sampleValue");`

## Build Json String

#### parser.listArgsProvided() populates the hashmap with the required and default variables

```
parser.listArgsProvided();
console.log(parser.argumentJson);
```
