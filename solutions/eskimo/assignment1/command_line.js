/**
 * @author AVINISH KUMAR
 * @college BIT MESRA
 */


//Stores all commands
var commandList=[];

//Stores Command Name
var commandName={};

//Stores smallCommand Name
var commandsmallName={};

//Stores the argument in JSON format
var argument_JSON={};

/**
* Parser Class
*/
class Parser
{

    /**
    * @constructor
    */
    constructor()
    { 

        //To check two Exclusive commands doesn't get together 
        this.isSetExclusive= new Array(100).fill("0");

        //help command :- print how object needs to be created and all commands with descroption
        var help_obj=
        {
            command:"help",
            describe:"HELP",
            handler:()=>{

                console.log("How to add commands:-");
                console.log("command: command name (string)");
                console.log("describe: description (string)");
                console.log("demandOption: Value needed or not (boolean)");
                console.log("type: input type for command (string) ");
                console.log("handler: function needed to be executed (function)");
                console.log();
                console.log("Commands:- ")
                this.commandList.forEach(command_available => {
                    console.log(command_available.command+": "+command_available.describe);
                });
            }
        }

        commandList.push(help_obj);

        //set the command name
        commandName["help_obj"]=0;
    }

    /**
     * Add commands to commandList
     * @param {JSON_object} input_command
     */
    add_command(input_command)
    {
        if(!this.correctCommand(input_command.command))
        {
            throw new Error('Enter correct command');
        }

        if(!this.correctType(input_command.type))
        {
            throw new Error('Enter correct type for command '+input_command.command);
        }

        if(!this.correctDemandOption(input_command.demandOption))
        {
            throw new Error('Enter correct demandOption for command '+input_command.command);
        }

        if(input_command.describe==null)
        {
            throw new Error('Enter command description for command '+input_command.command);
        }

        if(!this.isString(input_command.describe.replace(/ /g,'')))
        {
            throw new Error('Enter command description in correct format for command '+input_command.command);
        }

        if(input_command.ExclusiveIndex!=null)
        {
            //Checks ExclusiveIndex fromat & range
            if(!Number.isInteger(input_command.ExclusiveIndex) || input_command.ExclusiveIndex>=100)
                throw new Error('Enter correct ExclusiveIndex for command '+input_command.command);
        }

        if(input_command.type==null)
        {
            input_command.type="string";
        }

        if(input_command.demandOption==null)
            input_command.demandOption=false;

        //Checks for two command woth same name
        if(commandName[input_command.command]==1)
        {
            throw new Error(input_command.command+' Command already exists');
        }
        
        //Checks for smallCommand Input
        if(input_command.smallCommand!=null && (!this.correctCommand(input_command.smallCommand) || commandsmallName[input_command.smallCommand]!=null))
        {
            throw new Error('Enter correct samllCommand for command '+input_command.command);
        }

        commandList.push(input_command);

        //assing bot name and small to index of commandList
        commandName[input_command.command]=commandList.length-1;

        if(input_command.smallCommand!=null)
        {
            commandsmallName[input_command.smallCommand]=commandName[input_command.command];
        }
        // console.log(commandList[1]);
    }

    /**
     * Executes the commands
     */
    execute()
    {
        //process.argv returns all input arguments && slice(2) for removing first two unwanted arguments 
        var input_arg=process.argv.slice(2);
        
        input_arg.forEach((val) => {

            if(val.startsWith("--") || val.startsWith("-"))
            {
                var command_available;

                //For Name
                if(val.startsWith("--"))
                {
                    //Silces the "--" from argument
                    val=val.slice(2);

                    //Checks that a command exists in the commandList
                    if(commandName[(val.split("=")[0])]==null)
                        throw new Error("Command "+val.split("=")[0]+" does not exist");


                    command_available=commandList[commandName[(val.split("=")[0])]];
                }
                
                //For smallName
                else if(val.startsWith("-"))
                {
                    val=val.slice(1);

                    //Checks that a command exists in the commandList
                    if(commandsmallName[(val.split("=")[0])]==null)
                        throw new Error("Command "+val.split("=")[0]+" does not exist");


                    command_available=commandList[commandsmallName[(val.split("=")[0])]];
                }

                if(command_available.ExclusiveIndex!=null)
                {
                    //Checks if this command has previously occured or not 
                    if(this.isSetExclusive[command_available.ExclusiveIndex]!="0")
                    {
                        throw new Error("The "+command_available.command+" and "+this.isSetExclusive[command_available.ExclusiveIndex]+" arguments cannot be used together.");
                    }
                    else
                    {
                        //Sets index EclusiveIndex of isSetExclusive with command name
                        this.isSetExclusive[command_available.ExclusiveIndex]=command_available.command;
                    }
                }

                if(command_available.demandOption)
                {
                    if(!val.includes("="))
                    {
                        throw new Error("The '--"+command_available.command+"' argument is required, but missing from input.");
                    }

                    //Takes the value of argument
                    val=val.split("=")[1];

                    //Checks the command type
                    var command_type=command_available.type;

                    if(command_type=='string')
                    {
                        if(this.isString(val))
                        {
                            var command_obj= command_available.command;
                            argument_JSON[command_obj]=val;
                        }
                        else
                        {
                            throw new Error(Incorrect_Argument_Message(command_available.command));
                        }
                    }

                    else if(command_type=='number')
                    {
                        if(this.isNumber(val))
                        {
                            var command_obj= command_available.command;
                            argument_JSON[command_obj]=val;
                        }

                        else
                        {
                            throw new Error(Incorrect_Argument_Message(command_available.command));
                        }
                    }

                    else
                    {
                        if(this.isBoolean(val))
                        {
                            var command_obj= command_available.command;
                            argument_JSON[command_obj]=val;
                        }

                        else
                        {
                            throw new Error(Incorrect_Argument_Message(command_available.command));
                        }
                    }

                    //Checks for handler of command and execute it
                    if(command_available.handler!=null)
                        command_available.handler.apply();
                }    

            }

            else
            {
                throw new Error("Wrong Argument: ",val);
            }
        });
    }

    /**
     * Prints the JSON
     */
    display()
    {
        console.log(argument_JSON);
    }

    /**
     * Checks if type is correct
     */
    correctType(type)
    {
        if(type!='number' && type!='string' && type!='boolean' && type!=null)
            return false;
        return true;
    }

    /**
     * Checks if DemandOption is correct
     */
    correctDemandOption(demandOption)
    {
        if(demandOption!=true && demandOption!=false && demandOption!=null)
            return false;
        return true;
    }

    /**
     * Checks if command is correct
     */
    correctCommand(command)
    {
        if(command==null || ('0'<=command[0] && command[0]<='9'))
            return false;
        return true;
    }

    /**
     * Checks if value is string
     * @param {*} value 
     */
    isString(value)
    {
        if(value.match("^[A-z]+$"))
            return true;

        return false;
    }

    /**
     * Checks if value is number
     * @param {*} value 
     */
    isNumber(value)
    {
        if(value.match("^[0-9]+$"))
            return true;

        return false;
    }

    /**
     * Checks if value is boolean
     * @param {*} value 
     */
    isBoolean(value)
    {
        if(value=='true' || value=='false')
            return true;

        return false;
    }

    /**
     * Error message for Incorrect Argument
     * @param {string} command 
     */
    Incorrect_Argument_Message(command)
    {
        throw new Error("Enter correct argument for command "+command);
    }
}

//Exports the class Parser
module.exports =new Parser;