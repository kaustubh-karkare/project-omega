package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"strings"
	"validate"
)

// JSONItem is Container for storing JSON item
type JSONItem struct {
	key, value string
}

// Parser is a struct to implement OOPS type operation
type Parser struct {
	keystore map[string]validate.KeyProperty
}

// AddKey adds new argument to supported arguments
func (parser Parser) AddKey(key string, prop validate.KeyProperty) {

	parser.keystore[key] = prop
}

// AddKeyProperty adds argument properties to KeyProperty container
func AddKeyProperty(datatype string, mandatory, found bool) validate.KeyProperty {

	var prop validate.KeyProperty
	prop.Datatype = datatype
	prop.Mandatory = mandatory
	prop.Found = found
	return prop
}

// ErrorPrint return the appropriate error
func ErrorPrint(errorItem, errorType string) error {

	switch errorType {

	case "FormatError":
		err := "Error: Argument " + errorItem + " has incorrect format"
		return errors.New(err)

	case "ExistenceError":
		err := "Error: Key " + errorItem + " is not a supported Argument"
		return errors.New(err)

	case "TypeError":
		var item JSONItem
		item.key, item.value = strings.Split(errorItem, "=")[0], strings.Split(errorItem, "=")[1]
		err := "Error: value for the " + item.key + " must be " + item.value
		return errors.New(err)

	case "MandatoryError":
		err := "Error: required argument " + errorItem + " is missing from input"
		return errors.New(err)

	default:
		return errors.New("Error Encountered")
	}
}

// ParseApp converts the input into JSON form
func (parser Parser) ParseApp(args []string) (string, error) {

	// jsonkey stores and maps the key, value pair having correct format
	jsonkey := make(map[string]string)

	for id := 0; id < len(args); id++ {

		argCheck := validate.FormatCheck(args[id])
		if argCheck == false {
			return "", ErrorPrint(args[id], "FormatError")
		}

		var item JSONItem
		item.key, item.value = strings.Split(args[id], "=")[0], strings.Split(args[id], "=")[1]

		keyCheck := validate.ExistenceCheck(item.key, parser.keystore)
		if keyCheck == false {
			return "", ErrorPrint(item.key, "ExistenceError")
		}

		valueCheck := validate.TypeCheck(item.value, parser.keystore[item.key].Datatype)
		if valueCheck == false {
			return "", ErrorPrint(item.key+"="+parser.keystore[item.key].Datatype, "TypeError")
		}

		// Changing the Found property of key to True
		prop := parser.keystore[item.key]
		prop.Found = true
		parser.keystore[item.key] = prop
		jsonkey[strings.Split(item.key, "--")[1]] = item.value
	}

	// This Loop checks the presence of manadatroy keys
	for key, val := range parser.keystore {
		if val.Mandatory == true && val.Found == false {
			return "", ErrorPrint(key, "MandatoryError")
		}
	}

	// Converting the map values to JSON
	jsonOutput, _ := json.Marshal(jsonkey)
	return string(jsonOutput), nil
}

func main() {

	args := os.Args[1:]

	parser := new(Parser)
	// keystore stores and maps the permissible keys to it's value's property
	parser.keystore = make(map[string]validate.KeyProperty)
	parser.AddKey("--id", AddKeyProperty("Integer", true, false))
	parser.AddKey("--name", AddKeyProperty("String", true, false))
	parser.AddKey("--age", AddKeyProperty("Integer", false, false))
	parser.AddKey("--roll", AddKeyProperty("AlphaNumeric", false, false))
	jsonResult, err := parser.ParseApp(args)

	if err != nil {
		fmt.Println(err)
	} else {
		fmt.Println(jsonResult)
	}
}
