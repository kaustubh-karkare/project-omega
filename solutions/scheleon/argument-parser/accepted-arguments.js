const parser = require("./parser");

parser.addArgument("w", "weight", true, "Number", 100);
parser.addArgument("j", "jojo", true, "Boolean", false);
parser.listArgsProvided();

console.log(parser.argumentJson);