
## Resources

- Look into how build automation tools like [Make](https://www.gnu.org/software/make/) or [Buck](https://buckbuild.com/) work. This will help you get a sense of how large projects are compiled and tested.
- Look into the various ways to detect file system changes. Note that while there exist platform-specific subscription-based mechanisms, you will not be using them for the assignment below. This is just knowledge that you should have.


## Graded Assignment

- Write a program that detects changes in one or more files / directories, and then performs an action in response to it.
- You are not allowed to use any library that will detect changes for you. You should only use the basic file-system API provided by your language.
- You can take input via CLI arguments, or through a dot-file configuration, like:
```
{
	watch: ["src/*.cpp"],
	action: ["g++ -o final.exe src/*.cpp"]
}
```
