package validate

import "testing"

func TestFormatCheck(t *testing.T) {

	functionName := "FormatCheck"

	testcases := []struct {
		testInput string
		expect    bool
	}{
		{"--key=value", true},
		{"--key=", false},
		{"--key", false},
		{"--key=value=", false},
	}

	for _, testcase := range testcases {

		_, _, result := FormatCheck(testcase.testInput)
		if result != testcase.expect {
			t.Errorf("Expected %t from %s for %s but got %t", testcase.expect, functionName, testcase.testInput, result)
		}
	}
}

func TestKeyValueSeperation(t *testing.T) {


	functionName := "FormatCheck"

	testcases := []struct {
		testInput, key, value string
	}{
		{"--key=value", "key", "value"},
		{"--k=v", "k", "v"},
		{"--key=v", "key", "v"},
		{"--k=value=", "k", "value"},
	}

	for _, testcase := range testcases {

		key, value, _ := FormatCheck(testcase.testInput)
		if key != testcase.key || value != testcase.value {
			t.Errorf("Expected %s and %s from %s for %s but got %s and %s", testcase.key, testcase.value, functionName, testcase.testInput, key, value)
		}
	}
}

func TestExistenceCheck(t *testing.T) {

	functionName := "ExistenceCheck"
	keystore := make(map[string]KeyProperty)
	var demoprop KeyProperty
	keystore["--id"] = demoprop

	testcases := []struct {
		testInput string
		expect    bool
	}{
		{"--id", true},
		{"--key", false},
	}

	for _, testcase := range testcases {

		result := ExistenceCheck(testcase.testInput, keystore)
		if result != testcase.expect {
			t.Errorf("Expected %t from %s for %s but got %t", testcase.expect, functionName, testcase.testInput, result)
		}
	}

}

func TestTypeCheck(t *testing.T) {

	functionName := "TypeCheck"

	testcases := []struct {
		testInput, dataType string
		expect              bool
	}{
		{"aBcDeF", "String", true},
		{"aBcDeF0123", "String", false},
		{"01234", "Integer", true},
		{"0123aBcDeF", "Integer", false},
		{"aBcD01234", "AlphaNumeric", true},
		{"0123abcdef=", "AlphaNumeric", false},
	}

	for _, testcase := range testcases {

		result := TypeCheck(testcase.testInput, testcase.dataType)
		if result != testcase.expect {
			t.Errorf("Expected %t from %s for %s but got %t", testcase.expect, functionName, testcase.testInput, result)
		}
	}

}
