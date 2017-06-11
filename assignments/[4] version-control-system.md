
## Resources

All large software projects use a version control system.
Read the [Git Parable](http://tom.preston-werner.com/2009/05/19/the-git-parable.html) and the [Pro Git book](https://git-scm.com/book/en/v2).

## Graded Assignment

And now, without looking at the code for any existing VCS, implement your own.
Assuming that the executable is called `vcs`, support at least the following commands:

```
vcs init
vcs status # Show the list of changed files.
vcs diff # Show the diffs of changed files.
vcs commit # Asks for a commit message, and then creates it.
vcs reset # Discard all changes since the last commit.
vcs log <commit-hash> # Show commit message + metadata
vcs checkout <commit-hash> # Load the specified commit.
```

Note: For the sake of simplicity, do not bother with the concept of a staging area.
