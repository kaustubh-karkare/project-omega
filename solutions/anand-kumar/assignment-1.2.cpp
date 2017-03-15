#include <bits/stdc++.h>
using namespace std;
//  Global vector storing the JSON converted data.
vector<pair<string, string> > json;
//  Attributes of the parameter.
struct parameter_node {
  string parameter_name;
  string parameter_shorthand;
  string parameter_data_type;
  pair<bool, string> parameter_data;
  set<string> parameter_exclusive_list;
  string parameter_help;
};
void parameter_declaration(vector<struct parameter_node> &parameter, string
    p_name, string p_shorthand, string p_data_type, string p_help) {
  struct parameter_node ob;
  ob.parameter_name = p_name;
  ob.parameter_shorthand = p_shorthand;
  ob.parameter_data_type = p_data_type;
  ob.parameter_help = p_help;
  ob.parameter_data.first = false;
  ob.parameter_data.second = '\n';
  parameter.push_back(ob);
}
//  Index of a parameter in the structure object vector
int find_index(vector<struct parameter_node> parameter, string dummy) {
  for (int i = 0; i < parameter.size(); ++i) {
	  if (parameter[i].parameter_name == dummy || 
		    parameter[i].parameter_shorthand == dummy) {
		  return i;
		}
	}
	return -1;
}
void create_exclusive_parameters(vector<struct parameter_node> parameter,
    string ex_list[], int s) {
  for (int i = 0; i < s; ++i) {
		int index = find_index(parameter, ex_list[i]);
		if (index == -1) {
			cout << "Undefined parameter\n" ;
			exit(1);
		}

		for (int j = 0; j < s; ++j) {
			if (i == j)
				continue;
			parameter[index].parameter_exclusive_list.insert(ex_list[j]);
		}
	}
}
//  Extract the string content without '-' at any index of argv
string extract_string(char *argv[], int index) {
  int i = 0;
	string curr_temp = argv[index];
	while (curr_temp[i] == '-')
		++i;
	string dummy;
	while (curr_temp[i] != '\n' && i < curr_temp.length() && curr_temp[i] != '=') {
		dummy +=  curr_temp[i];
		++i;
	}
	return dummy;
}
bool is_integer(string num) {
	bool is_integer = true;
	for (int i = 0; i < num.length() && is_integer; ++i) {
		if (!(num[i] >= '0' && num[i] <= '9'))
			is_integer = false;
	}
	return is_integer;
}
bool is_floating(string num)
{
	bool is_float = true;
	int decimal = 0;
	for (int i = 0; i < num.length() && is_float; ++i) {
		if (num[i] == '.') {
			++decimal;
			continue;
		}
		if (!(num[i] >= '0' && num[i] <= '9'))
			is_float = false;
	}
	if (decimal > 1)
		is_float = false;
	return is_float;
}
bool is_boolean(string num)
{
	if (num == "true" || num == "TRUE" || num == "True" || num == "false" ||
		    num == "FALSE" || num == "False")
		return true;
	else
		return false;
}
//	To check for the argument along with the parameter given by the user.
void parameter_argument(vector<struct parameter_node> parameter, int argc,
    char *argv[], int &index) {
	string dummy = extract_string(argv, index);
	int option_index = find_index(parameter, dummy);
	if (option_index == -1) {
		cout << dummy << " ";
		cout << "parameter does not exist\n";
		exit(1);
	}
	if (parameter[option_index].parameter_data.first == false) {
			string data_dummy;
			int k = 0;
			string curr_temp =  argv[index];
			while (k < curr_temp.length() && 
			    curr_temp[k] != '\n' && curr_temp[k] != '=') {
				++k;
			}
			if (k < curr_temp.length() && curr_temp[k] != '\n') {
				++k;
				while (k < curr_temp.length() && curr_temp[k] != '\n') {
					data_dummy += curr_temp[k];
					++k;
				}
				++index;
			}
			else {
				++index;
				data_dummy = extract_string(argv, index);
				++index;
			}	
		bool valid_data_type = true;
		if (parameter[option_index].parameter_data_type == "int") {
			valid_data_type = is_integer(data_dummy);
		}
		else if (parameter[option_index].parameter_data_type == "float") {
			valid_data_type = is_floating(data_dummy);
		}
		else if (parameter[option_index].parameter_data_type == "bool") {
			valid_data_type = is_boolean(data_dummy);
		}
		else {
			valid_data_type = true;
		}
		if (valid_data_type == false) {
			cout << "Argument is either invalid or not provided\n";
			exit(1);
		}
		json.push_back(make_pair(dummy, data_dummy));
		return;
	}
	++index;

}
//  To check if a command is valid or not.
bool check_command(vector<string> command_list, string dummy) {
	for (int i = 0; i < dummy.size(); ++i){
		if (dummy == command_list[i])
			return true;
	}
	return false;
}
// To check for exclusivity of parameters.
void exclusivity(vector<struct parameter_node> parameter) {
	for (int i = 0; i < json.size(); ++i) {
		string dummy = json[i].first;
		int index = find_index(parameter, dummy);
		for (int j = 0; j < json.size(); ++j) {
			if (i == j)
				continue;
			set <string> :: iterator it = 
			    parameter[index].parameter_exclusive_list.begin();
			int option_index = find_index(parameter, json[j].first);
			while (it != parameter[index].parameter_exclusive_list.end()) {
				if (*it == dummy) {
					cout<< dummy << " and " << *it << " cannot be together\n";
					exit(1);
				}
				++it;
			}
		}
	}
}
void help_function(vector<struct parameter_node> parameter) {
	for (int i = 0; i < parameter.size(); ++i) {
		cout << "--" << parameter[i].parameter_name << " -"<< 
		    parameter[i].parameter_shorthand << " " << 
		    parameter[i].parameter_help << endl;
	}
}
void display() {
	cout << "{ ";
	for (int i = 0; i < json.size() - 1; ++i) {
		cout << "\"" << json[i].first << "\":" << "\"" << json[i].second << "\",";
	}
	cout << "\"" << json[json.size() - 1].first << "\":" << 
	"\"" << json[json.size() - 1].second << "\"";
	cout << "}\n";
}
int main(int argc, char *argv[]) {
	vector<struct parameter_node> parameter;
	//	Input the parameter with the argument;
	//	Enter the parameter name, shorthand representaion(optional), data type and
	//	the help message to be displayed;
	//	Function definition:- 
	//	void parameter_declaration(vector <struct parameter_node> &parameter,
	//	    string p_name, string p_shorthand, string p_data_type, 
	//			string p_help);
	//	Data types supported are "int", "float", "bool", "string".
	//	The data type is case sensitive and by default all parameters are string. 	
	//	Test data
	parameter_declaration(parameter, "key", "\n", "int",
	    "--key to initialise key");
	parameter_declaration(parameter, "name", "\n", "string",
		  "--name to initilase name");
	//	Enter parameters here.
	//	...
	//	Input the exclusive list of elements
	//	Enter the list of mutually exclusive elements in an array of string.
	//	Also define the number of elements pushed in the array.
	//	Function definition:-
	//	void create_exclusive_parameters(
	//	vector <struct parameter_node> parameter, string ex_list[], int s);
	//	Test data 
	string ex_list[] = {"local", "remote"};
	create_exclusive_parameters(parameter, ex_list, 2);
	//	Enter mutually exclusive elements.
	//	...

	//	Enter the command list for the parser
	vector<string> command_list;
	//	Push back the command in the command list.
	//	Test data
	command_list.push_back("alpha");
	command_list.push_back("beta");
	//	Enter the commands here.
	//	...

	int index = 1;
	if (argc < 2) {
		cout << "No parameter or command given\n";
		exit(1);
	}
	int counter = 0;
	while (index < argc) {
		string curr_temp = argv[index];
		if (curr_temp == "-h" || curr_temp == "--help") {
				help_function(parameter);
				++index;
				continue;
		}
		//	If a parameter.
		if (curr_temp[0] == '-')
			parameter_argument(parameter, argc, argv, index);
		else {	
		  //	If a command or a sub command.
			string dummy = extract_string(argv, index);
			bool command_possible = check_command(command_list, dummy);
			if (command_possible == false) {
				cout << "Invalid command\n" ;
				exit(1);
			}
			string id = "\n";
			//  Primary command
			if (counter == 0) {
				json.push_back(make_pair("command", dummy));
				++counter;
			}
			//	Sub - command
			else {
				for (int i = 0; i < counter; ++i)
					id += "sub-";
				id += "command";
				json.push_back(make_pair(id, dummy));
			}
			++index;
		}
	}
	exclusivity(parameter);
	display();
	return 0;
}
