package argparse

import (
	"encoding/json"
	"errors"
	"strings"
	"validate"
)

// JSONItem is Container for storing JSON item
type JSONItem struct {
	key, value string
}

// Pair does this
type Pair struct {
	FirstKey, SecondKey string
}

// Parser is a struct to implement OOPS type operation
type Parser struct {
	keystore  map[string]validate.KeyProperty
	exclusive []Pair
}

// AddKey adds new argument to supported arguments
func (parser *Parser) AddKey(key, datatype, mandatory string) {

	var prop validate.KeyProperty
	if mandatory == "IS_MANDATORY" {
		prop = AddKeyProperty(datatype, true)
	} else {
		prop = AddKeyProperty(datatype, false)
	}
	parser.keystore[key] = prop
}

// AddExclusiveKeys stores the exclusive pair of keys
func (parser *Parser) AddExclusiveKeys(FirstKey, SecondKey string) {

	var pair Pair
	pair.FirstKey, pair.SecondKey = FirstKey, SecondKey
	parser.exclusive = append(parser.exclusive, pair)
}

// AddKeyProperty adds argument properties to KeyProperty container
func AddKeyProperty(datatype string, mandatory bool) validate.KeyProperty {

	var prop validate.KeyProperty
	prop.Datatype = datatype
	prop.Mandatory = mandatory
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

	case "ExclusiveKeysError":
		var pair Pair
		pair.FirstKey, pair.SecondKey = strings.Split(errorItem, "=")[0], strings.Split(errorItem, "=")[1]
		err := "Error: " + pair.FirstKey + " and " + pair.SecondKey + " cannot be used together"
		return errors.New(err)

	default:
		return errors.New("Error Encountered")
	}
}

// ParseApp converts the input into JSON form
func (parser Parser) ParseApp(args []string) (map[string]string, error) {

	// jsonMap stores and maps the key, value pair having correct format
	jsonMap := make(map[string]string)

	for id := 0; id < len(args); id++ {

		var item JSONItem
		var argCheck bool

		// item variable stores the key,value if format of argument is correct
		item.key, item.value, argCheck = validate.FormatCheck(args[id])
		if argCheck == false {
			return jsonMap, ErrorPrint(args[id], "FormatError")
		}

		keyCheck := validate.ExistenceCheck(item.key, parser.keystore)
		if keyCheck == false {
			return jsonMap, ErrorPrint(item.key, "ExistenceError")
		}

		valueCheck := validate.TypeCheck(item.value, parser.keystore[item.key].Datatype)
		if valueCheck == false {
			return jsonMap, ErrorPrint(item.key+"="+parser.keystore[item.key].Datatype, "TypeError")
		}

		// Storing key,value pair in map
		jsonMap[strings.Split(item.key, "--")[1]] = item.value
	}

	// This loop throws error if exclusive pair of keys exist together
	for id := 0; id < len(parser.exclusive); id++ {

		var pair Pair
		pair = parser.exclusive[id]
		pair.FirstKey, pair.SecondKey = strings.Split(pair.FirstKey, "--")[1], strings.Split(pair.SecondKey, "--")[1]
		_, FoundfirstKey := jsonMap[pair.FirstKey]
		_, FoundsecondKey := jsonMap[pair.SecondKey]

		if FoundfirstKey == true && FoundsecondKey == true {
			keys := parser.exclusive[id].FirstKey + "=" + parser.exclusive[id].SecondKey
			return jsonMap, ErrorPrint(keys, "ExclusiveKeysError")
		}

	}

	// This loop checks the presence of manadatroy keys
	for key, val := range parser.keystore {
		key = strings.Split(key, "--")[1]
		_, found := jsonMap[key]
		if val.Mandatory == true && found == false {
			return jsonMap, ErrorPrint("--"+key, "MandatoryError")
		}
	}

	return jsonMap, nil
}

// JSONConvert converts map into JSON
func JSONConvert(jsonMap map[string]string) string {

	jsonOutput, _ := json.Marshal(jsonMap)
	return (string(jsonOutput))
}

// InitParser creates new instance of parser structure
func InitParser() *Parser {

	// keystore stores and maps the permissible keys to it's value's property
	parser := new(Parser)
	parser.keystore = make(map[string]validate.KeyProperty)
	parser.exclusive = make([]Pair, 0, 10)

	return parser
}
