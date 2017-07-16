## Version Control System

### VCS Hash Objects
The vcs stores content in the form of hash objects.

#### Binary Large Objects(BLOB)

The blob class stores the following:
- `type` as 'blob'.
- `content` stores the raw content of the file.

The blob class has the method(s):
- `get_hash_value` method takes input the content or file path and returns the SHA-1 hash.  
- `get_content` method returns the raw content stored by the object.


#### Tree Objects

The tree class stores:
- `type` as 'tree'.

The tree class stores a number of entries, each entry stores, 
- `hash_reference` stores the SHA-1 hash pointer reference to a blob or a subtree
- `name` stores the file or directory name
- `mode` stores the file or directory mode.


The tree class has the following method(s):
- `get_hash_value` method returns a SHA-1 hash based on the contents of the tree entry.
- `get_content` method returns the tree entries.


#### Commit Objects

The commit class stores the follwoing:
- `type` as 'commit'.
- `root` stores the SHA-1 hash pointer reference to the root of the commit tree.
- `parents` stores a list of parents for the commit.
- `author_name` stores the author name.
- `author_email` stores the author email.
- `timestamp` stores the time of the commit.
- `message` stores the commit message.

The commit class has the method(s):

- `create_hash_objects` method recrsively explores the commit tree creating blob and tree hash objects.
- `get_hash_value` method returns the SHA-1 hash based on the current contents of the entry.
- `get_commit_tree` method returns the root of the current commit tree.


### .vcs Directory

The .vcs directory stores information about the repository contents. It stores the following files and directories.
- `objects` directory stores all the hash objects.
- `HEAD` stores the current SHA-1 pointer reference of the commit object on the current branch.
- `heads` stores the SHA-1 pointer reference of the commit object on different branches.
- `config` stores the repository attributes. It also stores the author name and email.


### VCS Methods

The vcs internals includes the following methods:

- `init` method takes input a directory path or by default uses the current directory path to create the .vcs directory. The init method initializes the HEAD file pointer reference as `None`.
- `get_files_and_directories` method takes input a commit tree and recursively traverses the tree to return a list of file and directory paths along with their SHA-1 hash as stored in the `.vcs/objects/`.
- `status` method takes input the SHA-1 pointer reference to a commit tree or by default uses the last commit on the branch. It calls `get_files_and_directories` method with the input SHA-1 hash and compares the list with the contents of the working directory to find the changed, created and deleted files.
- `diff` method takes input the path for an old and a new file and uses the Myers diff algorithm to compare the two files and outputs the result to the stdout.
- `write_tree` method considers the contents of the working directory to be the input. It recursively builds a tree and returns the root. The directories constitute the non leaf nodes and the files constitutes the leaf nodes of the tree.
- `commit` method takes input a commit message and calls `write_tree` method for the working directory and creates an instance of the commit hash object.
- `delete_working_directory` method deletes the current contents of the working directory.
- `build_working_directory` method takes input a tree and recursively build the working directory. The non leaf node are the directories and the leaf nodes are the files. The SHA-1 hash objects are used to get the contents of the files.
- `checkout` method takes input a pointer reference to a commit hash. It calls the `delete_working_directory` method and calls the `build_working_directory` method with the SHA-1 reference to the commit tree.
- `reset` method calls the `checkout` method with the SHA-1 hash commit reference of the last commit on the branch.
- `log` method takes input the pointer reference to a commit hash object and outputs the author name, author email, the timestamp and the commit message to the stdout. 
