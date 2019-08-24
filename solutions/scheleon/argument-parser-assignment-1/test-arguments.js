const parser = require("./parser");

parser.addArgument("w", "weight", true, "String", "hello");
parser.addArgument("j", "jojo", false, "Boolean", false);

console.log(parser.listArgsProvided());