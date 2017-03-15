
// add new argument entries here.
var argList = [];

// add aditional argument types here

argTypeEnum = {
   'String': 0,
   'Boolean': 1,
   'Int': 2,
   '+Int': 3, // represents + integers
};

function argBuilder(key, arg, type, required, position) {
   if(key === null){
      console.log(`ERROR: Key of argument ${arg} cannot be null`);
      process.exit(1);
   }
   if(!(type in argTypeEnum)){
      console.log(`ERROR: Invalid type of argument ${arg}`);
      process.exit(1);
   }
   var tempObj = {};
   tempObj.key = key;
   tempObj.arg = arg;
   tempObj.type = type;
   tempObj.position = position;
   tempObj.required = required;
   argList.push(tempObj);
}

function argParser(inputArgs) {

   for(var i = 0; i < inputArgs.length; i++) {
      var str = inputArgs[i];
      flag = 0;
      if(str.search('-') !== 0) {
         for(j = 0; j < argList.length; j++) {
            if(argList[j].position === i) {
               flag = 1;
               parsedJson[argList[j].key] = str;
            }
         }
         if(flag === 0) {
            console.log(`ERROR: Invalid argument '${str}' entered`);
            return;
         }
      }
      else {
         str = str.split('=');
         for(j = 0; j < argList.length; j++)
         {
            if(argList[j].arg === str[0]) {
               flag = 1;
               if(argTypeEnum[argList[j].type] === 0)  {
                  parsedJson[argList[j].key] = str[1];
               }
               else if(argTypeEnum[argList[j].type] === 1) {
                  parsedJson[argList[j].key] = true;
               }
               else if(argTypeEnum[argList[j].type] === 2) {
                  if(isNaN(str[1])) {
                     console.log(`ERROR: Invalid value of argument '${str[0]}'. Must be a positive integer`);
                     return;
                  }
                  else {
                     parsedJson[argList[j].key] = str[1];
                  }
               }
               else if(argTypeEnum[argList[j].type] === 3) {
                  if( isNaN(str[1]) || str[1] * 1 < 0) {
                     console.log(`ERROR: Invalid value of argument '${str[0]}'. Must be a positive integer`);
                     return;
                  }
                  else {
                     parsedJson[argList[j].key] = str[1];
                  }
               }
            }
         }
         if(flag === 0) {
            console.log(`ERROR: Invalid argument '${str[0]}' entered`);
            return;
         }
      }
   }

   // validating. Add aditional validations here

   if(err.length > 0) {
      console.log('ERROR: ' + err);
      return;
   }
   for(i = 0; i < argList.length; i++) {
      if(argList[i].required === true && !(argList[i].key in parsedJson)) {
         console.log(`ERROR: Value of ${argList[i].arg}  required`);
         return;
      }
   }

   // output parsedJson

   console.log(parsedJson);
   return;
}

// add new arguments here in the format argBuilder('key', 'argumentName', 'type', 'required(Boolean)', position);

argBuilder('command', null, 'String', false, 0);
argBuilder('subcommand', null, 'String', false, 1);
argBuilder('key', '--key', '+Int', true, null);
argBuilder('name', '--name', 'String', false, null);
argBuilder('verbrose', '-v', 'Boolean', false, null);
argBuilder('local', '--local', 'Boolean', false, null);
argBuilder('remote', '--remote', 'Boolean', false, null);

var parsedJson = {};
var err = [], flag, j;
var inputArgs = process.argv.slice(2);

argParser(inputArgs);
