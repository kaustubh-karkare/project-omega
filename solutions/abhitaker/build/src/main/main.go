package main

import (
	"fmt"
	"make"
	"os"
)

func main() {

	phaseName := os.Args[1]
	err := make.Make(phaseName)

	if err != nil {
		fmt.Println(err)
	} else {
		fmt.Println("Succesfully executed")
	}

}
