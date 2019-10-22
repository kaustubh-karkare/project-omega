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
The `test.cpp` file declares the method:
```
void sort(vector<int> &list);
```
but does not implement it (ie - it does not #include them, so we need to manually link the object files). The cpp files in the `algorithms` directory provide 3 different implementations for that method, and the desired one is specified during the linking phase.
```
> cat algorithms/build.json
[
  {
    "name": "clean",
    "command": "rm -f *.o"
  },
  {
    "name": "sort_bubble",
    "command": "g++ -c sort_bubble.cpp"
  },
  {
    "name": "sort_merge",
    "command": "g++ -c sort_merge.cpp"
  },
  {
    "name": "sort_quick",
    "command": "g++ -c sort_quick.cpp"
  }
]

> cat build.json
[
  {
    "name": "clean",
    "deps": ["algorithms/clean"],
    "command": "rm -f test.o && rm -f test_*.exe"
  },
  {
    "name": "test",
    "command": "g++ -std=c++11 -c test.cpp"
  },
  {
    "name": "test_sort_bubble",
    "deps": ["test", "algorithms/sort_bubble"],
    "command": "g++ test.o algorithms/sort_bubble.o -o test_sort_bubble.exe && ./test_sort_bubble.exe"
  },
  {
    "name": "test_sort_merge",
    "deps": ["test", "algorithms/sort_merge"],
    "command": "g++ test.o algorithms/sort_merge.o -o test_sort_merge.exe && ./test_sort_merge.exe"
  },
  {
    "name": "test_sort_quick",
    "deps": ["test", "algorithms/sort_quick"],
    "command": "g++ test.o algorithms/sort_quick.o -o test_sort_quick.exe && ./test_sort_quick.exe"
  },
  {
    "name": "test_all",
    "deps": ["test_sort_bubble", "test_sort_merge", "test_sort_quick"]
  }
]
```
The "build.json" files contain a list of "actions". The build automation tool should be able to explore the given directory structure, create the "action graph", and be capable of executing actions like:
```
alias bat="python3 build_automation_tool.py"

> bat test_all  # compiles, links and runs the code
Bubble Sort Latency = 1276817
Merge Sort Latency = 93676
Quick Sort Latency = 3105

> bat clean  # deletes all generated files
```
The execution of an action is defined as the execution of all dependency actions, and only then running the associated command.

## Part 2

Instead of performing the actions one-at-a-time in some sequence, your tool should:
* Avoid duplication of work (eg - executing "test_all" naively will perform "test" thrice, but it should only happen once).
* Perform independent actions in parallel when possible (eg - the "test_*" actions can be performed simultaneously).

Do not use multi-threading here: you can poll the status of multiple processes from a single thread.

## Part 3

Until now, the developer was forced to manually trigger the tests. The final step is to do it automatically, whenever any source file is modified ([example](https://webpack.js.org/configuration/watch/)).
```
bat test_all --watch
```
If the `algorithms/sort_merge.cpp` files was updated by a text editor, your tool should detect this (without using external libraries like [this one](https://github.com/emcrisostomo/fswatch)), recompile only `algorithms/sort_merge.o` and `test.o` (because the other object files will not change), link everything together and finally run only that test. Feel free to add support for new attributes in the action data structure.
