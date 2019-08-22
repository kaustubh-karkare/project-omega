# ArgParse

ArgParse is a library written in **GO** to parse command line options, and print them as JSON.


How to install
----------

 * Create a new folder and copy the `src` folder into it

 * cd into the created folder

 * change the value of environment variable `$GOPATH` to current directory

    ```sh
    $ export GOPATH=$(pwd)
    ```

 * Build the file `main.go` present in folder `argparse` inside `src` folder. This will compile the package **main** and all its dependencies

    ```sh
    $ go build src/argparse/main.go
    ```

 * Install the compiled package using the following command

    ```sh
    $ go install argparse
    ```

* This will create a new folder `bin` with executable named **argparse** inside it.

How to use
----------

Some of the example usage:

```sh
$ ./argparse --id=1 --name=abhishek --roll=be1058416 --age=21
{"age":"21","id":"1","name":"abhishek","roll":"be1058416"}
    

$ ./argparse --id=1 --name=abhishek --roll=be1058416 --age=21a
 Error: value for the --age must be Integer
   

$ ./argparse --name=abhishek --roll=be1058416 --age=21
Error: required argument --id is missing from input
   

$ ./argparse --id=1 --name=abhishek --like=coding
Error: Key --like is not a supported Argument
    
    
$ ./argparse --id --name=abhishek
Error: Argument --id has incorrect format
```

How to run test
---------------

In order to run the test made for pacakge `validate`, run the following command inside `validate` folder:

```sh
$ go test
```
