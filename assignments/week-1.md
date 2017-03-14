## Problem 1.1

- Stop using Windows. Install Ubuntu. Start getting used to it.
- Dual-boot is acceptable in case you still want to play games.

## Problem 1.2

Since we're going to be using the command line a lot, let's start with that. Write a library to parse command line options, and print them as JSON. It should at least support the following inputs:

```
# Basic Usage
./test --key=12345 --name=kaustubh
{"key": "value", "name": "kaustubh"}

# Validation
./test --key=cat
Error: The value for the '--key' argument must be a positive integer.
./test
Error: The '--key' argument is required, but missing from input.
./test --local --remote
Error: The "--local" and "--remote" arguments cannot be used together.

# Positional Arguments & Short Names
./test alpha beta -V
{"command": "alpha", "subcommand": "beta", "verbose": True}
```

Do not use an existing library (such as those mentioned below) to do the heavy lifting for you, since it would defeat the purpose of this exercise. However, once you have completed your implementation, then I'd recommend reading about the APIs provided by [Python's argparse module](https://docs.python.org/3/library/argparse.html), [JavaScript's commander module](https://www.npmjs.com/package/commander), etc. Your goal here is to be confident that you can implement all the features listed there, even if you don't actually write the code for them (although doing so is a bonus). This way, you have knowledge about how different languages deal with this problem. Additionally, if something exists in one language, but not in another, you would know that it is a valid usecase. In fact you could be the one to build it in your language!

## Problem 1.3

Take a screenshot of your Facebook newsfeed. Reproduce it from scratch using only HTML & CSS (no JavaScript). Do not use any external libraries / stylesheets. Use dummy data to avoid sharing unnecessary information, since I only care about the structure/look of the page. It doesn't have to be pixel-perfect, since there is a point of diminishing returns, but the goal here is to teach you enough HTML such that you can understand the page source for a website when you need to. Additionally, this knowledge will be useful in subsequent assignments.
