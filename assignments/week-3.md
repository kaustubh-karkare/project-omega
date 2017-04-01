## Problem 3.1

Implement a regular expression engine. It should at least be able to support the following cases:

```
regexp.check("abcde", "abcde") // true
regexp.check("a\d?\w+\s*e", "abcde") // true
regexp.check("^a[b-k]{2}$", "abcde") // false
```

## Problem 3.2

- Let's assume that you have a directory that contains a C++ program, consisting of multiple files.
- Write a utility that detects any change in the contents of that directory (adding / removing / updating files). And whenever a change is detected, the C++ program is automatically recompiled.
- You are not allowed to use any library that will detect changes for you. You should only use the basic file-system API provided by your language.
