## General Instructions

* Submit your solutions as pull-requests to the `solutions` subdirectory in this repository. Make sure you check out the instructions specified there too.
* The number in the square brackets (ranging from 1-5) indicates my estimate of the difficulty of the problem.
* If you are concerned that you don't know a particular technology / language required to solve a problem, good. Use this opportunity to learn about it. If you can prove that a problem is too easy because of past experience, let me know, and I'll give you a harder problem.
* I recommend using Python or JavaScript (since I'm most familiar with them right now). However, you are free to choose any language you wish, as long as it is not something that makes code deliberately hard to read. If I don't know it, I will find someone who can review your code in my place, or else study the language and then review it myself.

## Coding Instructions


1. If I do not provide sample input/output in the problem, make reasonable assumptions. If I do, they are still just guidelines, so feel free to make reasonable changes.
    * Your goal isn't to pass some automated test-case checker: instead, it is to build something that will be __intuitively useful__ to other people, and so use your best judgement.
2. Please abide by the [style guide for your preferred language](https://google.github.io/styleguide/).
    * Why? Code is written only once, but read many many times, and so we want to optimize for that. If everyone follows the same conventions while writing code, it makes other people's code look like your own, and therefore, easier to understand.
    * A good analogy is that writing code without following a style guide is like using texting language in professional communication ("whr r u", instead of "Where are you?"). No one will take you seriously. Which is why this needs to become a habit ASAP.
    * Feel free to use a linter program that will ensure that your code meets the stylistic expectations.
3. Please create useful variable / function names.
    * When you're working with larger codebases, no one has the time to read all the code. Which means that you have to infer reasonable behavior based purely on names. And using proper descriptive variable / function names is the first step in making that possible. Not doing so would mean that other engineers cannot trust your code, which is not a situation you want to put yourself in.
    * Ask yourself: Is it possible to figure out what this variable contains based on just the name? If no, then it means that your variable doesn't have a good name. Avoid abbreviations if possible, since they introduce ambiguity, forcing the reader to figure out what you meant based on context (eg - `cmp` could mean `compare`, `comparator`, `compulsory`, etc). In almost all cases, `temp` (along with all its variants) is a bad name, because it tells me nothing about what it contains.
    * Similarly: Given just the function name and appropriate context, if you ask someone else to implement this function, will their code match yours (adjusting for minor differences)? If no, then your function doesn't have a good name. One important observation here is to never do something inside a function that isn't expected by just reading the name (eg - your `check` function should never print anything).
4. Please write well-structured code with clean abstractions.
    * What does that mean? The person reading your code should know how it works based purely on an understanding of the problem, and the API you provide. The fact that one does not have to read the internals of your code to understand it, is nice consequence of making the reasonable choice at every point. And this is extremely valuable while debugging complex systems.
    * Additionally, make sure that your code is resuable: that it solves more than just the exact problem you are working on right now. In real life, requirements are always changing, and you want to make sure you can handle that with minimal effort. To simulate that, I will always evaluate your code at a higher standard than the problem statement given to you.
5. In order to verify that the code works as intended, write comprehensive unit tests.
    * When I review your code, the tests are the first thing I look at. Without them, I have no reason to believe that the rest of your code works.
