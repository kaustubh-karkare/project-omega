/**
 * @author AVINISH KUMAR
 * @college BIT MESRA
 */


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
        //Stores all commands
        this.commandList=[];

        //Stores the argument in JSON format
        this.argument_JSON={};

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

        //Adds help to commandList
        this.commandList.push(help_obj);
    }

    /**
     * Add commands to commandList
     * @param {JSON_object} add_command
     */
    command(add_command)
    {
        //Checks command fromat
        if(!this.correctCommand(add_command.command))
        {
            throw new Error('Enter correct command');
        }

        //Checks type fromat
        if(!this.correctType(add_command.type))
        {
            throw new Error('Enter correct type for command '+add_command.command);
        }

        //Checks DemandOption fromat
        if(!this.correctDemandOption(add_command.demandOption))
        {
            throw new Error('Enter correct demandOption for command '+add_command.command);
        }

        //Checks for describe
        if(add_command.describe==null)
        {
            throw new Error('Enter command description for command '+add_command.command);
        }

        //Checks if decribe is a string
        if(!this.isString(add_command.describe.replace(/ /g,'')))
        {
            throw new Error('Enter command description in correct format for command '+add_command.command);
        }

        //Check ExclusiveIndex is set 
        if(add_command.ExclusiveIndex!=null)
        {
            //Checks ExclusiveIndex fromat & range
            if(!Number.isInteger(add_command.ExclusiveIndex) || add_command.ExclusiveIndex>=100)
                throw new Error('Enter correct ExclusiveIndex for command '+add_command.command);
        }

        //Sets type to string if null
        if(add_command.type==null)
        {
            add_command.type="string";
        }

        //Sets type to string if null
        if(add_command.demandOption==null)
            add_command.demandOption=false;
        
        //Adds the command to commandList
        this.commandList.push(add_command);
    }

    /**
     * Executes the commands
     */
    execute()
    {
        //process.argv returns all input arguments && slice(2) for removing first two unwanted arguments 
        var input_arg=process.argv.slice(2);
        
        //Checks for each input_arg
        input_arg.forEach((val) => {

            //Checks argument must start with "--" 
            if(val.startsWith("--"))
            {
                //Silces the "--" from argument
                val=val.slice(2);

                //Stores the current argument in a var
                var input_command=val;

                //Checks that a command exists in the commandList
                var command_exist=0;

                //Checks commandList for a match
                this.commandList.forEach((command_available)=>{

                    //Checks if argument starts with a command specified
                    if(val.startsWith(command_available.command))
                    {
                        //Sets command_exists true
                        command_exist=1;
                        
                        //Checks if this command have a exclusive property
                        if(command_available.ExclusiveIndex!=null)
                        {
                            //Checks if this command has previously occured or not 
                            if(this.isSetExclusive[command_available.ExclusiveIndex]!="0")
                            {
                                //Both commands can not occur together
                                console.log("The "+command_available.command+" and "+this.isSetExclusive[command_available.ExclusiveIndex]+" arguments cannot be used together.")
                                return;
                            }
                            else
                            {
                                //Sets index EclusiveIndex of isSetExclusive with command name
                                this.isSetExclusive[command_available.ExclusiveIndex]=command_available.command;
                            }
                        }

                        //Checks for command demandOption
                        if(command_available.demandOption)
                        {
                            //Checks for '=' in argument if demandOption is true
                            if(!val.includes("="))
                            {
                                //Error if argument doesn't have a value
                                console.log("The '--"+command_available.command+"' argument is required, but missing from input.");
                                return;
                            }

                            //Takes the value of argument
                            val=val.split("=")[1];

                            //Checks the command type
                            var command_type=command_available.type;

                            if(command_type=='string')
                            {
                                //Checks that value must be a string
                                if(this.isString(val))
                                {
                                    //Add the argument in JSON
                                    var command_obj= command_available.command;
                                    this.argument_JSON[command_obj]=val;
                                }
                                else
                                {
                                    //Incorrect Argument Error
                                    this.Incorrect_Argument_Message(command_available.command);
                                    return;
                                }
                            }

                            else if(command_type=='number')
                            {
                                //Checks that value must be a number
                                if(this.isNumber(val))
                                {
                                    //Add the argument in JSON
                                    var command_obj= command_available.command;
                                    this.argument_JSON[command_obj]=val;
                                }

                                else
                                {
                                    //Incorrect Argument Error
                                    this.Incorrect_Argument_Message(command_available.command);
                                    return;
                                }
                            }

                            else
                            {
                                //Checks that value must be a number
                                if(this.isBoolean(val))
                                {
                                    //Add the argument in JSON
                                    var command_obj= command_available.command;
                                    this.argument_JSON[command_obj]=val;
                                }

                                else
                                {
                                    //Incorrect Argument Error
                                    this.Incorrect_Argument_Message(command_available.command);
                                    return;
                                }
                            }

                            
                        }

                        //Checks for handler of command and execute it
                        if(command_available.handler!=null)
                            command_available.handler.apply();
                    }    
                })

                //Check for command existance
                if(command_exist==0)
                {
                    //Error message
                    console.log("Command "+input_command+" does not exist");
                    return;
                }

            }

            else
            {
                //Error if argument is wrong
                console.log("Wrong Argument: ",val);
            }
        });
    }

    /**
     * Prints the JSON
     */
    display()
    {
        console.log(this.argument_JSON);
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
     * Errorxmessage for Incorrect Argument
     * @param {string} command 
     */
    Incorrect_Argument_Message(command)
    {
        console.log("Enter correct argument for command "+command);
    }
}

//Exports the class Parser
module.exports =new Parser;