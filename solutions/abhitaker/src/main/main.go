package main

import (
	"argparse"
	"fmt"
)

func main() {

	testInput := []string{"--id=1", "--name=abhishek", "--roll=be1058416", "--age=21"}

	var parser = argparse.InitParser()
	parser.AddKey("--id", "Integer", "IS_MANDATORY")
	parser.AddKey("--name", "String", "IS_MANDATORY")
	parser.AddKey("--age", "Integer", "NOT_MANDATORY")
	parser.AddKey("--roll", "AlphaNumeric", "NOT_MANDATORY")
	parser.AddExclusiveKeys("--roll", "--age")
	parser.AddExclusiveKeys("--name", "--age")
	
	jsonMap, err := parser.ParseApp(testInput)

	if err != nil {
		fmt.Println(err)
	} else {
		// Converting the map values to JSON
		jsonOutput := argparse.JSONConvert(jsonMap)
		fmt.Println(jsonOutput)
	}
}
