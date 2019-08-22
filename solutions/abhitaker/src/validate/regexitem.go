package validate

import (
	"regexp"
)

// KeyProperty is a Container for storing Permissible Key's property
type KeyProperty struct {
	Datatype         string
	Mandatory, Found bool
}

// JSONItem is Container for storing JSON item
type JSONItem struct {
	key, value string
}

// FormatCheck performs format check on argument
func FormatCheck(itemArg string) bool {

	matched, _ := regexp.MatchString("^--([a-zA-Z0-9]+)=([a-zA-Z0-9]+$)", itemArg)
	return matched
}

// ExistenceCheck check if given key is present in argument list
func ExistenceCheck(itemKey string, keystore map[string]KeyProperty) bool {

	_, found := keystore[itemKey]
	return found
}

// TypeCheck checks if Json value is same as datatype
func TypeCheck(itemValue, dataType string) bool {

	switch dataType {

	case "String":
		matched, _ := regexp.MatchString("^([a-zA-Z]+)$", itemValue)
		return matched

	case "Integer":
		matched, _ := regexp.MatchString("^([0-9]+$)", itemValue)
		return matched

	case "AlphaNumeric":
		matched, _ := regexp.MatchString("^([a-zA-Z0-9]+$)", itemValue)
		return matched

	default:
		return false
	}
}
