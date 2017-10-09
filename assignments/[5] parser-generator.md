
## Resources

- Warning: You should complete the Regular Expression Engine assignment before attempting this one.
- Watch this series of lectures on YouTube about [Compiler Design](https://www.youtube.com/watch?v=Qkwj65l_96I&index=1&list=PLEbnTDJUr_IcPtUXFy2b1sGRPsLFMghhS). For what it's worth, this is one of the best teachers available online.

## Graded Assignment

Write a program that can take the following grammar as input:
```
expression = term ('+' expression)?;
term = factor ('*' term)?;
factor = /[0-9]+/ | '(' expression ')';
```
And based on that, generate an SLR(1) parser that can translate `2*3+(4+5)*6` into a JSON structure like the following:
```
{
  "name": "expression",
  "children": [
    {
      "name": "term",
      "children": [
        {
          "name": "factor",
          "children": [{"value": "2"}]
        },
        {
          "value": "*"
        },
        {
          "name": "factor",
          "children": [{"value": "3"}]
        }
      ]
    },
    {
      "value": "+",
    },
    ...
  ]
}
```

For bonus points, generate an LALR(1) parser in a language **different** from the one used to analyse the input grammar.
