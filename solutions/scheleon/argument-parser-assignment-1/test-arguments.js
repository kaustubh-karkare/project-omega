const parser = require("./parser");

parser.addArgument("w", "weight", true, "String", "hello");
parser.addArgument("j", "jojo", true, "Boolean", false);
//parser.addArgument("j", "jojo", false, "Boolean", false);

parser.listArgsProvided(process.argv);
console.log(parser.argumentJson);