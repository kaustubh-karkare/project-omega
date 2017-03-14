var arg  = process.argv.slice(2);
var arg_cons = function(command, subcommand,key, name, local, remote, v)
{
   this.command  = command;
   this.subcommand = subcommand;
   this.name = name;
   this.key = key;
   this.local = local;
   this.remote = remote;
   this.verbrose = v;
};
var com_args = new arg_cons();
var err = [];

com_parser(arg, print_json);

function print_json(err){
   if(err.length!==0)
      console.log("ERROR\n"+err);
   else if(com_args.key === undefined)
      console.log("ERROR: Must have a key value");
   else console.log(com_args);
}

function com_parser(arg, callback){

   var i;
   for(i=0;i<arg.length;i++){
      arg[i]=arg[i].toLowerCase();

      if(arg[i].search('-') === -1){
         if(i === 0)
            com_args.command = arg[i];
         else if(i === 1)
            com_args.subcommand = arg[i];
         else
            err.push("Invalid argument at position");
      }
     else if(arg[i].search('=')!=-1){
         var strarr = arg[i].split('=');
         if(strarr[0] === '--key'){
            com_args.key = strarr[1];
            if( isNaN(strarr[1]) || strarr[1]*1<0 ){
               err.push("Invalid value of key. Must be a positive integer");
            }
         }
         else if(strarr[0] === '--name'){
            com_args.name = strarr[1];
         }
         else{
            err.push("Invalid argument passed");
         }
      }


      else if(arg[i] === '-v'){
         com_args.verbrose = true;
      }


      else if(arg[i] === '--local'){
         com_args.local = true;
         if(com_args.remote === true){
            err.push("Remote and Local cannot come together");
         }
      }


      else if(arg[i] === '--remote'){
         com_args.remote = true;
         if(com_args.local === true){
            err.push("Remote and Local cannot come together");
         }
      }
   }
   callback(err);
}
