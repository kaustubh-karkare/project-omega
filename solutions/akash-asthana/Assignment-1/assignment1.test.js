//USED JEST FOR TESTING THE PROJECT
const { extractArgumentName,
    extractArgumentValue,
    typeCheck,
    checkIfArgumentDefined,
    areRequiredArgumentsPresent,
    ifArgumentsCanBeUsedTogether,
    parseArgumentsIntoJSON } = require("./assignment1");

test("Should return the name of the argument passed", () => {
    expect(extractArgumentName("--key=212")).toEqual("key");
});

test('Should return value of the argument passed', () => {
    expect(extractArgumentValue("--name=akash")).toEqual("akash");
})

test('Should check valid type of the argument passed', () => {
    expect(typeCheck("key", "213jkbkj12")).toEqual(false)
})

test("Should check if given argument is defined", () => {
    expect(checkIfArgumentDefined("name")).toEqual(true)
});

test("Should check if given argument is defined", () => {
    expect(checkIfArgumentDefined("lastName")).toEqual(false);
});

test("Should check if given argument is defined", () => {
    expect(areRequiredArgumentsPresent(["key", "name"])).toEqual(true);
});

test("Should check if given argument is defined", () => {
    expect(ifArgumentsCanBeUsedTogether(["key", "name", "local", "remote"])).toEqual(false);
});




