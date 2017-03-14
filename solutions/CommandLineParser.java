/* JAVA Code to take Command Line Arguments and print them as JSON.
 Supports a command and a subcommand (both optional), a required integer
 argument 'key', an optional string argument 'name', a verbose argument and two
 mutually exclusive arguments, local and remote.

 Any arguments not used are not included in JSON.
 */
import java.util.*;
import java.util.HashMap;
import java.io.*;
import org.codehaus.jackson.map.ObjectMapper; //To convert HashMap to JSON string

// Class containing important attributes of each argument
class Argument{
  String full_name;
  char short_name;
  boolean is_optional;
  boolean is_mutually_exclusive;
  int group_id; //Group id of mutually exclusive arguments
}

class CommandLineParser {
  //stores the valid arguments along with their values
  static HashMap<String,String> input;
  //Array of argument type objects to store their predefined attributes. This program supports 7 arguments.
  static Argument arguments[] = new Argument[7];
  /*Boolean array to indicate if an element of a particular group has been already given as input.
    True indicates that no element of that group has yet been given as input.
    This program supports 1 such group.
  */
  static boolean group_verify[] = new boolean[1];

  //Constructor to initalise values
  public CommandLineParser(){
      input = new HashMap<String,String>();

      arguments[0] = new Argument();
      arguments[0].full_name = "key";
      arguments[0].short_name = 'K';
      arguments[0].is_optional = false;
      arguments[0].is_mutually_exclusive = false;
      arguments[0].group_id = -1; //-1 indicates that group_id is not valid for that argument.

      arguments[1] = new Argument();
      arguments[1].full_name = "name";
      arguments[1].short_name = 'N';
      arguments[1].is_optional = true;
      arguments[1].is_mutually_exclusive = false;
      arguments[1].group_id = -1;

      arguments[2] = new Argument();
      arguments[2].full_name = "local";
      arguments[2].short_name = 'L';
      arguments[2].is_optional = true;
      arguments[2].is_mutually_exclusive = true;
      arguments[2].group_id = 0;

      arguments[3] = new Argument();
      arguments[3].full_name = "remote";
      arguments[3].short_name = 'R';
      arguments[3].is_optional = true;
      arguments[3].is_mutually_exclusive = true;
      arguments[3].group_id = 0;

      arguments[4] = new Argument();
      arguments[4].full_name = "verbose";
      arguments[4].short_name = 'V';
      arguments[4].is_optional = true;
      arguments[4].is_mutually_exclusive = false;
      arguments[4].group_id = -1;

      arguments[5] = new Argument();
      arguments[5].full_name = "command";
      arguments[5].short_name = '0';  //no short name
      arguments[5].is_optional = true;
      arguments[5].is_mutually_exclusive = false;
      arguments[5].group_id = -1;

      arguments[6] = new Argument();
      arguments[6].full_name = "subcommand";
      arguments[6].short_name = '0'; //no short name
      arguments[6].is_optional = true;
      arguments[6].is_mutually_exclusive = false;
      arguments[6].group_id = -1;
      // initialising group_verify array to true.
      for(int i = 0; i < group_verify.length; i++)
        group_verify[i] = true;

    }
    //Method to validate the value of "--key" argument
      static boolean value_check(String value) {
        int val;
        try {
          val = Integer.parseInt(value);//Exception thrown if not an integer
          if(val<=0) {
            System.out.println("Error: The value for --key must be a positive integer");
            return false;
          }
          return true;
        }
        catch(Exception e) {
          System.out.println("Error: The value for --key must be a positive integer");
          return false;
        }

    }

    public static void main(String args[]) {
      CommandLineParser clp = new CommandLineParser();
      int positional_arguments = 0; //initialise
      int compulsory_arguments = 0; //initialise
      boolean is_valid = true; //keeps track if all arguments are valid
      for(int i = 0; i < args.length; i++) {
        if(args[i].startsWith("--")) {
          boolean invalid_argument = true; //to check if currently scanned argument matches with any of our stored arguments, initialised to true.
          String temp = args[i].substring(2);//removes "--" and saves the argument in temp

          for(int j = 0; j < 7; j++) {
            if(temp.startsWith(arguments[j].full_name)) { //if match is found
              invalid_argument = false; //The current argument matches with some predefined argument
              if(!arguments[j].is_optional)
                compulsory_arguments++; //If compulsory argument, then increase it's count by 1

              int index = temp.indexOf('='); //find if '=' is present in it
              if(index!=-1) {   //if present
                String value = temp.substring(index+1);
                input.put(arguments[j].full_name,value); //store the argument with it's value in "input" HashMap

                if(j==0) {  //if the argument is of "key" type then the value needs to be validated
                  is_valid = value_check(value); //returns true if validation is successful.
                }
              }

              else {  //if no '= ' sign is found
                if(!arguments[j].is_mutually_exclusive) {
                  input.put(arguments[j].full_name,"true");  //If not mutually exclusive then stores it in "input" with value true
                }
                else {
                  if(group_verify[arguments[j].group_id]) {   //Verification if found to be of mutually exclusuve type
                  input.put(arguments[j].full_name,"true");   //If passed verification then stored as true
                  group_verify[arguments[j].group_id] = false;
                }
                else {  //If verification not passed then error message will be printed
                  is_valid = false;
                  System.out.print("Error: The ");
                  for(int k = 0; k < 7;k++){
                      if(arguments[j].group_id == arguments[k].group_id)
                        System.out.print("--"+arguments[k].full_name+" ");
                  }
                  System.out.println("argument/arguments cannot be used together\n");
                }

              }
            }
          }
        }

          if(invalid_argument) {  //If matching predefined arguments are not found
            is_valid = false;
            System.out.println("Invalid argument - "+temp);
          }
        }

        else if(args[i].startsWith("-")) {  //The same processes are repeated if short name is scanned instead of full name
          String temp = args[i].substring(1);
          boolean invalid_argument = true;
          for(int j = 0; j < 7; j++) {
            if(temp.charAt(0) == arguments[j].short_name) {
              invalid_argument = false;
              if(!arguments[j].is_optional)
                compulsory_arguments++;

              int index = temp.indexOf('=');
              if(index!=-1) {
                String value = temp.substring(index+1);
                input.put(arguments[j].full_name,value);

                if(j==0) {
                  is_valid = value_check(value);
                }
              }
              else {
                if(!arguments[j].is_mutually_exclusive) {
                  input.put(arguments[j].full_name,"true");
                }
                else {
                  if(group_verify[arguments[j].group_id]) {
                  input.put(arguments[j].full_name,"true");
                  group_verify[arguments[j].group_id] = false;
                }
                else {
                  is_valid = false;
                  System.out.print("Error: The ");
                  for(int k = 0; k < 7;k++){
                      if(arguments[j].group_id == arguments[k].group_id)
                        System.out.print("--"+arguments[k].full_name+" ");
                  }
                  System.out.println("argument/arguments cannot be used together\n");
                }
              }
            }
          }
        }




          if(invalid_argument) {
            is_valid = false;
            System.out.println("Invalid argument - "+temp);
          }

        }

        else {  //if positional arguments are scanned. Maximum 2 positional arguemnts are supported.
            if(positional_arguments == 0) {
              input.put("command",args[i]);
              positional_arguments++;
            }
            else if(positional_arguments == 1){
              input.put("subcommand",args[i]);
              positional_arguments++;
            }
            else {
              is_valid = false;
              System.out.println("Too many postional arguments");
            }
        }
      }
      if(compulsory_arguments<1) {   //if all the compulsory arguments(here 1) are not scanned
        is_valid = false;
        System.out.print("Error: The ");
        for(int i=0;i<7;i++){
          if(!arguments[i].is_optional)
            System.out.print("--"+arguments[i].full_name+" ");
        }
        System.out.print("arguments/arguments is/are required, but missing from input\n");
      }

      if(is_valid) {
        //Converts "input" HashMap to JSON string using Jackson API if arguments are valid.
        ObjectMapper mapperObj = new ObjectMapper();
        try {
            String jsonResp = mapperObj.writeValueAsString(input);
            System.out.println(jsonResp); //Prints JSON String
        }
        catch (IOException e) {
            e.printStackTrace();
        }
      }
      //Prints help menu if argumets are invalid
      else {
        System.out.println("Help:\n [--key Positive Integer] [--name String] [--verbose] [--local] [--remote] [command] [subcommand]");
      }
    }
}
