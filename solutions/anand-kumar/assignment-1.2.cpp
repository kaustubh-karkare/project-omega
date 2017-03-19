#include <bits/stdc++.h>
using namespace std;

class parser {
 private:
  // Attributes of the parameter.
  struct parameter_node {
    string name;
    string shorthand;
    string data_type;
    string value;
    bool is_data_required;
    set<string> exclusive_list;
    string help_instruction;
  };
  int number_of_commands_recieved;
  vector<pair<string, string> > json;

 public:
  // Constructor for specifying instances at the time of creation
  parser() {
    number_of_commands_recieved = 0;
  } 
  // structure to store at any instance the parameter and the argument under
  // consideration

  struct parameter_and_argument_node {
    bool is_argument_available;
    string parameter_name;
    string parameter_argument;
  } parameter_and_argument;
  
  // Vector of object of struct parameter_node to store all parameters.

  vector<struct parameter_node> parameter_list;

  void argument_assignment(
    string name_argument, string data_type_argument, string argument_existence,
    string shorthand_argument);
  int find_index(string parameter);
  void create_exclusive_parameters_set(string ex_list[], int size_of_ex_list);
  void extract_parameter_and_argument(string current_parameter);
  bool is_integer(string num);
  bool is_floating(string num);
  bool is_boolean(string num);
  void if_valid_data_type(int parameter_index, string current_argument);
  void parameter_and_argument_parsing(string current_parameter);
  void check_exclusivity_of_json();
  void help_function();
  void display_without_hyphen(string parameter);
  void display_json();
};

void parser::argument_assignment(
    string name_argument, string data_type_argument, string argument_existence,
    string shorthand_argument) {

  // Temporary object ob creation.

  struct parameter_node ob;
  ob.name = name_argument;
  ob.shorthand = shorthand_argument;
  ob.data_type = data_type_argument;
  if (argument_existence == "compulsory") {
    ob.is_data_required = true;
  }
  else {
    ob.is_data_required = false;
  }
  if (ob.is_data_required == true) {
    ob.help_instruction = "Compulsory argument";
  }
  else {
    ob.help_instruction = "Optional argument";
  }
  ob.help_instruction += " of type " + data_type_argument;
  parameter_list.push_back(ob);
}

// Index of the parameter in the parameter_list
int parser::find_index(string current_parameter) {
  if (current_parameter.length() == 0) {
    return -1;
  }
  for (int i = 0; i < parameter_list.size(); ++i) {
    if (
      parameter_list[i].name == current_parameter ||
      parameter_list[i].shorthand == current_parameter ) {
      return i;
    }
  }
  return -1;
}

void parser::create_exclusive_parameters_set
    (string ex_list[], int size_of_ex_list) {
  if (size_of_ex_list == 0) {
    return;
  }
  for (int i = 0; i < size_of_ex_list; ++i) {
    int index = find_index(ex_list[i]);
    if (index == -1) {
      display_without_hyphen(ex_list[i]);
      cout << " is an undefined parameter\n" ;
      exit(1);
    }
    for (int j = 0; j < size_of_ex_list; ++j) {
      if (i == j) {
        continue;
      }
      parameter_list[index].exclusive_list.insert(ex_list[j]);
    }
  }
}

bool parser::is_integer(string num) {
  bool is_integer = true;
  for (int i = 0; i < num.length() && is_integer; ++i) {
    if (!(num[i] >= '0' && num[i] <= '9')) {
      is_integer = false;
    }
  }
  return is_integer;
}

bool parser::is_floating(string num) {
  bool is_float = true;
  int decimal = 0;
  for (int i = 0; i < num.length() && is_float; ++i) {
    if (num[i] == '.') {
      ++decimal;
      continue;
    }
    if (!(num[i] >= '0' && num[i] <= '9')) {
      is_float = false;
    }
  }
  if (decimal > 1) {
    is_float = false;
  }
  return is_float;
}

bool parser::is_boolean(string num) {
  if (
    num == "true" ||
    num == "TRUE" ||
    num == "True" ||
    num == "false" ||
    num == "FALSE" ||
    num == "False") {
    return true;
  }
  else {
    return false;
  }
}

void parser::if_valid_data_type(int parameter_index, string current_argument) {
  bool valid_data_type = true;
  if (parameter_list[parameter_index].data_type == "int") {
    valid_data_type = is_integer(current_argument);
  }
  else if (parameter_list[parameter_index].data_type == "float") {
    valid_data_type = is_floating(current_argument);
  }
  else if (parameter_list[parameter_index].data_type == "bool") {
    valid_data_type = is_boolean(current_argument);
  }
  else {
    // By default all are considered to be string.
    valid_data_type = true;
  }
  if (valid_data_type == false) {
    display_without_hyphen(parameter_list[parameter_index].name);
    cout << " has an invalid data\n";
    exit(1);
  }
}

void parser::extract_parameter_and_argument(
    string current_parameter) {
  int i = 0;
  string current_extracted_parameter;

  // If the input is of the form --key=1234
  // Extract only parameter i.e --key

  while (i < current_parameter.length() && current_parameter[i] != '=') {
      current_extracted_parameter +=  current_parameter[i];
    ++i;
  }
  ++i;
  string current_extracted_argument;
  while (i < current_parameter.length()) {
      current_extracted_argument += current_parameter[i];
    ++i;
  }
  parameter_and_argument.parameter_name =
      current_extracted_parameter;
  parameter_and_argument.parameter_argument =
      current_extracted_argument;
  if (current_extracted_argument.length() == 0) {
    parameter_and_argument.is_argument_available = false;
  }
  else {
    parameter_and_argument.is_argument_available = true;
  }
}
// To check for the argument along with the parameter given by the user.
void parser::parameter_and_argument_parsing(string current_parameter) {
  if (current_parameter == "--help" || current_parameter == "-h") {
    help_function();
  }
  extract_parameter_and_argument(current_parameter);
  int parameter_index = find_index(parameter_and_argument.parameter_name);
  if (parameter_index == -1) {
    display_without_hyphen(parameter_and_argument.parameter_name);
    cout <<" is undefined\n";
    exit(1);
  }
  parameter_list[parameter_index].value = 
      parameter_and_argument.parameter_argument;
  // If a command or a sub-command
  
  if (current_parameter.length() > 0 && current_parameter[0] != '-') {
    string current_id_value ;
    for (int i = 0; i < number_of_commands_recieved; ++i) {
      current_id_value += "sub-";
    }
    current_id_value += "command";
    json.push_back(make_pair(current_id_value, current_parameter));
    ++number_of_commands_recieved;
    return;
  }
  if (parameter_and_argument.is_argument_available == false) {
    if (parameter_list[parameter_index].is_data_required == true) {
      display_without_hyphen(parameter_list[parameter_index].name);
      cout << "is missing argument\n";
    }
    else {
      json.push_back(make_pair(parameter_list[parameter_index].name,
          "null"));
    }
  }
  else {
    if_valid_data_type(parameter_index,
        parameter_list[parameter_index].value);
    json.push_back(make_pair(parameter_list[parameter_index].name,
        parameter_list[parameter_index].value));
  }
}

// To check for check_exclusivity_of_json of parameters.

void parser::check_exclusivity_of_json() {
  for (int i = 0; i < json.size(); ++i) {
    // The first element of json pair contains the parameter name.
    string current_parameter = json[i].first;
    // If the parameter is a command the second element of the json pair is the
    // parameter.
    if (current_parameter.length() > 0 && current_parameter[0] != '-') {
      current_parameter = json[i].second;
    }
    int parameter_index = find_index(current_parameter);
    for (int j = 0; j < json.size(); ++j) {
      if (i == j) {
        continue;
      }
      set <string>::iterator it =
        parameter_list[parameter_index].exclusive_list.begin();
      int current_parameter_index = find_index(json[j].first);
      while (it != parameter_list[parameter_index].exclusive_list.end()) {
        if (*it == json[j].first) {
          display_without_hyphen(json[i].first);
          cout << " and ";
          display_without_hyphen(*it);
          cout  << " cannot be used simultaeously\n";
          exit(1);
        }
        ++it;
      }
    }
  }
}

void parser::help_function() {
  for (int i = 0; i < parameter_list.size(); ++i) {
    cout << parameter_list[i].name;
    if (parameter_list[i].shorthand.length() > 0) {
      cout << " " << parameter_list[i].shorthand;
    }
    cout << " " << parameter_list[i].help_instruction << "\n";
  }
  exit(1);
}

void parser::display_without_hyphen(string parameter) {
  int i = 0;
  while (i < parameter.length() && parameter[i] == '-' && i <= 1) {
    ++i;
  }
  cout << parameter.substr(i, parameter.length() - i);
}
void parser::display_json() {
  if (json.size() == 0) {
    return;
  }
  cout << "{";
  for (int i = 0; i < json.size() - 1; ++i) {
    cout << "\"";
    display_without_hyphen(json[i].first);
    cout <<  "\": " << "\"" << json[i].second << "\", ";
  }
  cout << "\"";
  display_without_hyphen(json[json.size() - 1].first);
  cout << "\": " << "\"" << json[json.size() - 1].second << "\"";
  cout << "}\n";
}


int main(int argc, char *argv[]) {
  // Test class parser object
  class parser parser_object;

  // Input the parameter with the argument;
  // Enter the parameter name, data type, existence status of argument,
  // shorthand representaion(optional).
  // Function definition:-
  // void argument_assignment(
  // string name_argument, string data_type_argument,
  // string argument_existence, string shorthand_argument);
  // Data types supported are "int", "float", "bool", "string", "none"
  // The data type is case sensitive and by default all parameters are string.
  // Argument existence states are "optional" and "compulsory"
  // Test data

  parser_object.argument_assignment("--help", "none", "optional", "-h");
  parser_object.argument_assignment("--key", "int", "compulsory", "\n");
  parser_object.argument_assignment("--name", "string", "optional", "\n");
  parser_object.argument_assignment("alpha", "none", "optional", "\n");
  parser_object.argument_assignment("beta", "none", "optional", "\n");
  parser_object.argument_assignment("--local", "bool", "optional", "\n");
  parser_object.argument_assignment("--remote", "bool", "optional", "\n");

  // Enter parameters here.
  // ...

  // Input the exclusive list of elements
  // Enter the list of mutually exclusive elements in an array of string.
  // Also define the number of elements pushed in the array.
  // Function definition:-
  // void create_exclusive_parameters_set(string ex_list[], int size);
  // Test data

  string ex_list[] = {"--local", "--remote"};
  parser_object.create_exclusive_parameters_set(ex_list,
      sizeof(ex_list) / sizeof(ex_list[0]));

  // Enter mutually exclusive elements.
  // ...

  int index = 1;
  if (argc < 2) {
    cout << "No parameter or command given\n";
    exit(1);
  }
  while (index < argc) {
    string current_parameter = argv[index];
    parser_object.parameter_and_argument_parsing(current_parameter);
    ++index;
  }
  parser_object.check_exclusivity_of_json();
  parser_object.display_json();
  return 0;
}
