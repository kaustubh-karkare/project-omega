
// add new argument entries here

var command_args  = [
   {
      key: 'command',
      arg: null,
      type: 'String',
      required: false,
      position: 0
   },
   {
      key: 'subcommand',
      arg: null,
      type: 'String',
      required: false,
      position: 1
   },
   {
      key: 'key',
      arg: '--key',
      type: 'Int',
      required: true,
      position: null
   },
   {
      key: 'name',
      arg: '--name',
      type: 'String',
      required: false,
      position: null
   },
   {
      key: 'verbrose',
      arg: '-v',
      type: 'Boolean',
      required: false,
      position: null
   },
   {
      key: 'local',
      arg: '--local',
      type: 'Boolean',
      required: false,
      position: null
   },
   {
      key: 'remote',
      arg: '--remote',
      type: 'Boolean',
      required: false,
      position: null
   }
];

var parsed_json = {};
var err = [],flag,j;
var entered_args = process.argv.slice(2);


function print_json(err){
   if(err)
   {
      console.log('ERROR: ' + err);
      return;
   }
   for(i=0;i<command_args.length;i++)
   {
      if(command_args[i].required === true && !(command_args[i].key in parsed_json)){
         console.log( "ERROR: Value of " + command_args[i].arg + " required");
         return;
      }
   }
   console.log(parsed_json);
   return;
}

arg_parser(entered_args, print_json);

function arg_parser(entered_args, callback){
   for(var i=0; i<entered_args.length; i++){
      var str = entered_args[i];
      flag = 0;
      if(str.search('-') === -1){
         for(j=0; j<command_args.length; j++)
         {
            if(command_args[j].position === i){
               flag = 1;
               parsed_json[command_args[j].key] = str;
            }
         }
         if(flag === 0){
            console.log(`ERROR: Invalid argument '${str}' entered`);
            return;
         }
      }
      else{
         str = str.split('=');
         for(j=0; j<command_args.length; j++)
         {
            if(command_args[j].arg === str[0]){
               flag=1;
               if(command_args[j].type === 'String'){
                  parsed_json[command_args[j].key] = str[1];
               }
               else if(command_args[j].type === 'Boolean'){
                  parsed_json[command_args[j].key] = true;
               }
               else if(command_args[j].type === 'Int'){
                  if( isNaN(str[1]) || str[1]*1<0 ){
                     console.log(`ERROR: Invalid value of argument '${str[0]}'. Must be a positive integer`);
                     return;
                  }
                  else{
                     parsed_json[command_args[j].key] = str[1];
                  }
               }
            }
         }
         if(flag === 0){
            console.log(`ERROR: Invalid argument '${str[0]}' entered`);
            return;
         }
      }
   }
   callback();
}
