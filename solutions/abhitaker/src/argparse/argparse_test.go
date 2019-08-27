package argparse

import (
	"reflect"
	"testing"
)

func TestParserJSON(t *testing.T) {

	var parser = InitParser()
	parser.AddKey("--id", "Integer", "IS_MANDATORY")
	parser.AddKey("--name", "String", "IS_MANDATORY")
	parser.AddKey("--age", "Integer", "NOT_MANDATORY")
	parser.AddKey("--roll", "AlphaNumeric", "NOT_MANDATORY")

	testInput := []string{"--id=1", "--name=abhishek", "--roll=be1058416", "--age=21"}
	testExpect := map[string]string{"age": "21", "id": "1", "name": "abhishek", "roll": "be1058416"}
	jsonMap, _ := parser.ParseApp(testInput)

	functionName := "ParseApp"
	equal := reflect.DeepEqual(testExpect, jsonMap)
	if equal == false {
		t.Errorf("Expected %s from %s but got %s", testExpect, functionName, jsonMap)
	}

}

func TestParserTypeError(t *testing.T) {

	var parser = InitParser()
	parser.AddKey("--id", "Integer", "IS_MANDATORY")
	parser.AddKey("--name", "String", "IS_MANDATORY")
	parser.AddKey("--age", "Integer", "NOT_MANDATORY")
	parser.AddKey("--roll", "AlphaNumeric", "NOT_MANDATORY")

	testInput := []string{"--id=1", "--name=abhishek", "--roll=be1058416", "--age=21a"}
	testExpect := "Error: value for the --age must be Integer"
	_, err := parser.ParseApp(testInput)

	functionName := "ParseApp"
	if err.Error() != testExpect {
		t.Errorf("Expected \"%s\" from %s but got \"%s\"", testExpect, functionName, err)
	}
}

func TestParseMandatoryError(t *testing.T) {

	var parser = InitParser()
	parser.AddKey("--id", "Integer", "IS_MANDATORY")
	parser.AddKey("--name", "String", "IS_MANDATORY")
	parser.AddKey("--age", "Integer", "NOT_MANDATORY")
	parser.AddKey("--roll", "AlphaNumeric", "NOT_MANDATORY")

	testInput := []string{"--name=abhishek", "--roll=be1058416", "--age=21"}
	testExpect := "Error: required argument --id is missing from input"
	_, err := parser.ParseApp(testInput)

	functionName := "ParseApp"
	if err.Error() != testExpect {
		t.Errorf("Expected \"%s\" from %s but got \"%s\"", testExpect, functionName, err)
	}
}

func TestExclusiveKeysError(t *testing.T) {

	var parser = InitParser()
	parser.AddKey("--id", "Integer", "IS_MANDATORY")
	parser.AddKey("--name", "String", "IS_MANDATORY")
	parser.AddKey("--age", "Integer", "NOT_MANDATORY")
	parser.AddKey("--roll", "AlphaNumeric", "NOT_MANDATORY")
	parser.AddExclusiveKeys("--roll", "--age")

	testInput := []string{"--id=1", "--name=abhishek", "--roll=be1058416", "--age=21"}
	testExpect := "Error: --roll and --age cannot be used together"
	_, err := parser.ParseApp(testInput)

	functionName := "ParseApp"
	if err.Error() != testExpect {
		t.Errorf("Expected \"%s\" from %s but got \"%s\"", testExpect, functionName, err)
	}
}
