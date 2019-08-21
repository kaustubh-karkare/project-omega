const Parser = require('./parser');

const parser = new Parser();

const options = [
  {
    smallArg: 'k',
    largeArg: '--key',
    description: 'key value, must be + integer',
    defaultValue: undefined,
    type: parser.type.POSITIVE_INTEGER,
    isRequired: true,
  },
  {
    smallArg: '-n',
    largeArg: '--name',
    description: '',
    defaultValue: undefined,
    type: parser.type.STRING,
    isRequired: false,
  },
  {
    smallArg: '-l',
    largeArg: '--local',
    description: '',
    defaultValue: undefined,
    type: parser.type.BOOLEAN,
    isRequired: false,
  },
  {
    smallArg: '-r',
    largeArg: '--remote',
    description: '',
    defaultValue: undefined,
    type: parser.type.BOOLEAN,
    isRequired: false,
  },
];

options.forEach((option) => {
  parser.setOption(option);
});

parser.setMutuallyExclusive(['--local', '--remote']);

test('PassKeyNameResultsInOutput', () => {
  const argv = ['node', 'parser.js', '--key=12345', '--name=kaustubh'];
  expect(parser.parseOpts(argv)).toEqual(
      {
        key: '12345',
        name: 'kaustubh',
        local: undefined,
        remote: undefined,
      }
  );
});

test('PassKeyNameLocalResultsInOutput', () => {
  const argv =
   ['node', 'parser.js', '--key=12345', '--name=kaustubh', '--local'];
  expect(parser.parseOpts(argv)).toEqual(
      {
        key: '12345',
        name: 'kaustubh',
        local: true,
        remote: undefined,
      }
  );
});

test('PassInvalidArgumentResultsException', () => {
  const argv = ['node', 'parser.js',
    '--key=12345', '--name=kaustubh', '--local', '--2ojdeij'];
  expect(() => parser.parseOpts(argv)).toThrow(Parser.InvalidArgumentException);
});

test('PassInvalidArgumentTypeResultsException', () => {
  const argv = ['node', 'parser.js',
    '--key=fwfef', '--name=kaustubh'];
  expect(() => parser.parseOpts(argv))
      .toThrow(Parser.InvalidArgumentTypeException);
});

test('NotPassingRequiredArgumentResultsInException', () => {
  const argv = ['node', 'parser.js', '--name=kaustubh'];
  expect(() => parser.parseOpts(argv))
      .toThrow(Parser.MissingRequiredArgumentException);
});

test('PassingMutuallyExclusiveArgumentResultsInException', () => {
  const argv = ['node', 'parser.js', '--name=kaustubh', '--local', '--remote'];
  expect(() => parser.parseOpts(argv))
      .toThrow(Parser.MutuallyExclusiveArgumentsPassedException);
});
