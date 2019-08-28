const Parser = require('./parser');

const parser = new Parser();

const options = [
  {
    smallArg: 'k',
    largeArg: '--key',
    description: 'key value, must be + integer',
    type: parser.type.POSITIVE_INTEGER,
    isRequired: true,
  },
  {
    smallArg: '-n',
    largeArg: '--name',
    type: parser.type.STRING,
  },
  {
    smallArg: '-l',
    largeArg: '--local',
    type: parser.type.BOOLEAN,
  },
  {
    smallArg: '-r',
    largeArg: '--remote',
    type: parser.type.BOOLEAN,
  },
  {
    smallArg: '-c',
    largeArg: '--customdes',
    type: parser.type.BOOLEAN,
    dest: 'CUSTOMDEST1',
  },
  {
    smallArg: '-o',
    largeArg: '--options',
    type: parser.type.POSITIVE_INTEGER,
    nargs: 3,
  }
];

options.forEach((option) => {
  parser.addOption(option);
});

parser.setMutuallyExclusive(['--local', '--remote']);

test('Pass Key And Name Parses Correctly', () => {
  const argv = ['--key=12345', '--name=kaustubh'];
  expect(parser.parseOpts(argv)).toEqual(
      {
        key: ['12345'],
        name: ['kaustubh'],
      }
  );
});

test('Pass Key Name Local Parses Correctly', () => {
  const argv = ['--key=12345', '--name=kaustubh', '--local'];
  expect(parser.parseOpts(argv)).toEqual(
      {
        key: ['12345'],
        name: ['kaustubh'],
        local: [true],
      }
  );
});

test('Pass Invalid Argument Results Exception', () => {
  const argv = ['--key=12345', '--name=kaustubh', '--local', '--2ojdeij'];
  expect(() => parser.parseOpts(argv)).toThrow(Parser.InvalidArgumentException);
});

test('Pass Invalid Argument Type Results Exception', () => {
  const argv = ['--key=fwfef', '--name=kaustubh'];
  expect(() => parser.parseOpts(argv))
      .toThrow(Parser.InvalidArgumentTypeException);
});

test('Not Passing Required Argument Results In Exception', () => {
  const argv = ['--name=kaustubh'];
  expect(() => parser.parseOpts(argv))
      .toThrow(Parser.MissingRequiredArgumentException);
});

test('Passing Mutually Exclusive Argument Results In Exception', () => {
  const argv = ['--name=kaustubh', '--local', '--remote'];
  expect(() => parser.parseOpts(argv))
      .toThrow(Parser.MutuallyExclusiveArgumentsPassedException);
});

test('Pass Arg With Custom Dest Generates Correct KeyName In JSON', () => {
  const argv = ['--key=12345', '--name=kaustubh', '-c'];
  expect(parser.parseOpts(argv)).toEqual(
      {
        key: ['12345'],
        name: ['kaustubh'],
        CUSTOMDEST1: [true],
      }
  );
});

test('Pass correct number of arguments = nargs Parses Correctly', () => {
  const argv = ['--key=12345', '--name=kaustubh', '-o', '132', '123', '561'];
  expect(parser.parseOpts(argv)).toEqual(
      {
        key: ['12345'],
        name: ['kaustubh'],
        options: ['561', '123', '132'],
      }
  );
});

test('Pass Arg With Spaces and "=" parses correctly', () => {
  const argv = ['--key=12345', '--name=kaustubh', '-o', '132', '123', '561'];
  expect(parser.parseOpts(argv)).toEqual(
      {
        key: ['12345'],
        name: ['kaustubh'],
        options: ['561', '123', '132'],
      }
  );
});

test('Not passing required number of Args results in Exception', () => {
  const argv = ['--key=12345', '--name=kaustubh', '-o', '132', '123'];
  expect(() => parser.parseOpts(argv))
      .toThrow(Parser.InvalidNumberOfArgumentException);
});
