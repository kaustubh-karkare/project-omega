## Problem 1.1

- Stop using Windows. Install Ubuntu. Start getting used to it.
- Dual-boot is acceptable in case you still want to play games.

## Problem 1.2

Since we're going to be using the command line a lot, let's start with that. Write a program to parse command line options, and print them as JSON. It should at least support the following inputs:

```
# Basic Usage
./solution --key=12345 --name=kaustubh
{"key": "value", "name": "kaustubh"}

# Validation
./solution --key=cat
Error: The value for the '--key' argument must be a positive integer.
./solution
Error: The '--key' argument is required, but missing from input.
./solution --local --remote
Error: The "--local" and "--remote" arguments cannot be used together.

# Position Arguments & Short Names
./solution alpha beta -V
{"command": "alpha", "subcommand": "beta", "verbose": True}
```

In order to gain perspective on how different languages deal with this problem, I recommend reading about the API of [Python's argparse module](https://docs.python.org/3/library/argparse.html), [JavaScript's commander module](https://www.npmjs.com/package/commander), etc. That way, if something exists in one language, but not in another, you will know that the feature exists, and that someone just needs to build it. And that someone could be you!
