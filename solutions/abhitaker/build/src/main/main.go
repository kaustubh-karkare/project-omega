package main

import (
	"fmt"
	"make"
	//"os"
	"flag"
)

func main() {

	var buildFilename, root string
	var waitTime int
	var watch bool

	flag.StringVar(&root, "root", "", "Location of Directory from where to run make")
	flag.StringVar(& buildFilename, "buildfile", "build.json", "Name of the Build file name")
	flag.IntVar(& waitTime, "wait-time", 60, "Name of the Build file name")
	flag.BoolVar(&watch, "watch", false, "for enabling the watch feature")

	flag.Parse()
	BuildPhases := flag.Args()

	err := make.Make(root, buildFilename, waitTime, watch, BuildPhases)
	
	if err != nil {
		fmt.Println(err)
	} else {
		fmt.Println("Succesfully executed")
	}
	
}
