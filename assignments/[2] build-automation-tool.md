## Introduction

When working on large projects, the process of building and testing code might be fairly complex and involve making assumptions about the environment, running multiple commands in a specific sequence, etc. In order to ensure consistency in the process used by different developers, all of this build/test logic is expressed in "build configuration files" (one of many names for this concept), and then triggered by humans when needed during development.

Another benefit of a "build automation tool" is that it can be triggered by machines. In case of small projects, a pre-commit-hook could be configured to run all the tests, while for larger projects (where this would take too long) we could have a separate set of machines responsible for periodically building and testing everything.

Examples = [Make](http://matt.might.net/articles/intro-to-make/), [Buck](https://buck.build/), [NPM](https://docs.npmjs.com/misc/scripts).

## Part 1

You are going to create your own build automation tool.
What follows is a description of how it will work.

Consider a project with the following file structure:
```
algorithms/
    build.json
    sort_bubble.cpp
    sort_merge.cpp
    sort_quick.cpp
build.json
test.cpp
```
The `test.cpp` files imports the 3 sorting algorithms and then verifies their correctness. It only contains the declarations of the sorting methods, not the definitions. It does not #include them, so we need to manually link the object files.
```
> cat algorithms/build.json
[
  {
    "name": "clean",
    "command": "rm -f *.o"
  },
  {
    "name": "sort_bubble",
    "files": ["sort_bubble.cpp"],
    "command": "g++ -c sort_bubble.cpp"
  },
  {
    "name": "sort_merge",
    "files": ["sort_merge.cpp"],
    "command": "g++ -c sort_merge.cpp"
  },
  {
    "name": "sort_quick",
    "files": ["sort_quick.cpp"],
    "command": "g++ -c sort_quick.cpp"
  }
]

> cat build.json
[
  {
    "name": "clean",
    "deps": ["algorithms/clean"],
    "command": "rm -f test.o && rm -f test.exe"
  },
  {
    "name": "test",
    "files": ["test.cpp"],
    "command": "g++ -std=c++11 -c test.cpp"
  },
  {
    "name": "run",
    "deps": ["test", "algorithms/sort_bubble", "algorithms/sort_merge", "algorithms/sort_quick"],
    "command": "g++ algorithms/sort_bubble.o algorithms/sort_merge.o algorithms/sort_quick.o test.o -o test.exe && ./test.exe"
  }
]
```
The build automation tool we want should be able to explore the given directory structure, create the necessary dependency graphs, and be capable of running commands like:
```
# alias build="python3 build.py"
# build <name> (where name matches something in the build.json files)

build clean  # deletes all object/exe files
build run    # compiles, links and runs the code
```

## Part 2

Until now, the developer was forced to manually trigger the tests. The next step is to do it automatically, whenever any source file is modified ([example](https://webpack.js.org/configuration/watch/)).
```
build run --watch
```
If the `algorithms/sort_merge.cpp` files was updated by a text editor, your tool should detect this (without using external libraries like [this one](https://github.com/emcrisostomo/fswatch)), recompile only `algorithms/sort_merge.o` and `test.o` (because the other object files will not change), link everything together and finally run the test.
