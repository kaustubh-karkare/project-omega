package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"validate"
)

// JSONItem is Container for storing JSON item
type JSONItem struct {
	key, value string
}

// AddKey adds new argument to supported arguments
func AddKey(key string, prop validate.KeyProperty, keystore map[string]validate.KeyProperty) map[string]validate.KeyProperty {

	keystore[key] = prop
	return keystore
}

// AddKeyProperty adds argument properties to KeyProperty container
func AddKeyProperty(datatype string, mandatory, found bool) validate.KeyProperty {

	var prop validate.KeyProperty
	prop.Datatype = datatype
	prop.Mandatory = mandatory
	prop.Found = found
	return prop
}

// ErrorPrint outputs the appropriate error
func ErrorPrint(errorItem, errorType string) {

	switch errorType {

	case "FormatError":
		fmt.Printf("Error: Argument %s has incorrect format\n", errorItem)

	case "ExistenceError":
		fmt.Printf("Error: Key %s is not a supported Argument\n", errorItem)

	case "TypeError":
		var item JSONItem
		item.key, item.value = strings.Split(errorItem, "=")[0], strings.Split(errorItem, "=")[1]
		fmt.Printf("Error: value for the %s must be %s\n", item.key, item.value)

	case "MandatoryError":
		fmt.Printf("Error: required argument %s is missing from input\n", errorItem)

	default:
		return
	}
}

func main() {

	// keystore stores and maps the permissible keys to it's value's property
	keystore := make(map[string]validate.KeyProperty)
	// jsonkey stores and maps the key, value pair having correct format
	jsonkey := make(map[string]string)
	keystore = AddKey("--id", AddKeyProperty("Integer", true, false), keystore)
	keystore = AddKey("--name", AddKeyProperty("String", true, false), keystore)
	keystore = AddKey("--age", AddKeyProperty("Integer", false, false), keystore)
	keystore = AddKey("--roll", AddKeyProperty("AlphaNumeric", false, false), keystore)

	args := os.Args[1:]
	for id := 0; id < len(args); id++ {

		argCheck := validate.FormatCheck(args[id])
		if argCheck == false {
			ErrorPrint(args[id], "FormatError")
			return
		}

		var item JSONItem
		item.key, item.value = strings.Split(args[id], "=")[0], strings.Split(args[id], "=")[1]

		keyCheck := validate.ExistenceCheck(item.key, keystore)
		if keyCheck == false {
			ErrorPrint(item.key, "ExistenceError")
			return
		}

		valueCheck := validate.TypeCheck(item.value, keystore[item.key].Datatype)
		if valueCheck == false {
			ErrorPrint(item.key+"="+keystore[item.key].Datatype, "TypeError")
			return
		}

		// Changing the Found property of key to True
		prop := keystore[item.key]
		prop.Found = true
		keystore[item.key] = prop
		jsonkey[strings.Split(item.key, "--")[1]] = item.value
	}

	// This Loop checks the presence of manadatroy keys
	for key, val := range keystore {
		if val.Mandatory == true && val.Found == false {
			ErrorPrint(key, "MandatoryError")
			return
		}
	}

	// Converting the mao values to JSON
	jsonOutput, _ := json.Marshal(jsonkey)
	fmt.Println(string(jsonOutput))
}
