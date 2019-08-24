//USED JEST FOR TESTING THE PROJECT
const { extractArgumentName, extractArgumentValue, typeCheck } = require("./assignment1");

test("Should return the name of the argument passed", () => {
    expect(extractArgumentName("--key=212")).toEqual("key");
});

test("Should return the name of the argument passed", () => {
    expect(extractArgumentName("--name=akash")).toEqual("name");
});


test('Should return value of the argument passed', () => {
    expect(extractArgumentValue("--name=akash")).toEqual("akash");
})

test('Should return value of the argument passed', () => {
    expect(extractArgumentValue("--name=2434")).toEqual("2434");
})


test('Should check valid type of the argument passed', () => {
    expect(typeCheck("key", "213jkbkj12")).toEqual(false)
})

test('Should check valid type of the argument passed', () => {
    expect(typeCheck("name", "kaustubh")).toEqual(true)
})
