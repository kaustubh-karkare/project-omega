# Examples
```
$ node parser.js --key=12345 --name=kaustubh
{ key: '12345',
  name: 'kaustubh',
  local: undefined,
  remote: undefined }

$ node parser.js --key=12345 --name=kaustubh --local
{ key: '12345', name: 'kaustubh', local: true, remote: undefined }

$ node parser.js --key=12345 --name=kaustubh --local --2ojdeij
Error: "--2ojdeij" is not a valid argument

$ node parser.js --key=cat                  
Error: The value for the "--key" argument must be a positive-integer.

$ node parser.js 
Error: The '--key' argument is required, but missing from input.

$ node parser.js --local --remote
Error: The '--key' argument is required, but missing from input.

$ node parser.js --local --remote --key=12345
Error: The "--local" and "--remote" arguments cannot be used together.
```
