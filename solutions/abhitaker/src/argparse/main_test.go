package main

import (
	"testing"
	"validate"
)

func TestParserJSON(t *testing.T) {

	parser := new(Parser)
	parser.keystore = make(map[string]validate.KeyProperty)
	parser.AddKey("--id", AddKeyProperty("Integer", true, false))
	parser.AddKey("--name", AddKeyProperty("String", true, false))
	parser.AddKey("--age", AddKeyProperty("Integer", false, false))
	parser.AddKey("--roll", AddKeyProperty("AlphaNumeric", false, false))

	testInput := []string{"--id=1", "--name=abhishek", "--roll=be1058416", "--age=21"}
	testExpect := "{\"age\":\"21\",\"id\":\"1\",\"name\":\"abhishek\",\"roll\":\"be1058416\"}"
	jsonResult, _ := parser.ParseApp(testInput)

	functionName := "ParseApp"
	if jsonResult != testExpect {
		t.Errorf("Expected %s from %s but got %s", testExpect, functionName, jsonResult)
	}
	
}

func TestParserTypeError(t *testing.T) {

	parser := new(Parser)
	parser.keystore = make(map[string]validate.KeyProperty)
	parser.AddKey("--id", AddKeyProperty("Integer", true, false))
	parser.AddKey("--name", AddKeyProperty("String", true, false))
	parser.AddKey("--age", AddKeyProperty("Integer", false, false))
	parser.AddKey("--roll", AddKeyProperty("AlphaNumeric", false, false))

	testInput := []string{"--id=1", "--name=abhishek", "--roll=be1058416", "--age=21a"}
	testExpect := "Error: value for the --age must be Integer"
	_, err := parser.ParseApp(testInput)

	functionName := "ParseApp"
	if err.Error() != testExpect {
		t.Errorf("Expected \"%s\" from %s but got \"%s\"", testExpect, functionName, err)
	}
}

func TestParseMandatoryError(t *testing.T) {

	parser := new(Parser)
	parser.keystore = make(map[string]validate.KeyProperty)
	parser.AddKey("--id", AddKeyProperty("Integer", true, false))
	parser.AddKey("--name", AddKeyProperty("String", true, false))
	parser.AddKey("--age", AddKeyProperty("Integer", false, false))
	parser.AddKey("--roll", AddKeyProperty("AlphaNumeric", false, false))

	testInput := []string{"--name=abhishek", "--roll=be1058416", "--age=21"}
	testExpect := "Error: required argument --id is missing from input"
	_, err := parser.ParseApp(testInput)

	functionName := "ParseApp"
	if err.Error() != testExpect {
		t.Errorf("Expected \"%s\" from %s but got \"%s\"", testExpect, functionName, err)	
	}
}	
