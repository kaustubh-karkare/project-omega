
## Topics

- If you're not already familiar with Regular Expressions, learn about them.


## Practice Problems

- Write regexes to validate basic strings like email addresses, dates, etc.


## Graded Assignment

Implement a regular expression engine. It should at least be able to support the following cases:

```
regex.check("abcde", "abcde") // true
regex.check("a\d?\w+\s*e", "abcde") // true
regex.check("^a[b-k]{2}$", "abcde") // false
```
