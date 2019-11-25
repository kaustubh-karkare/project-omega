var command_line=require("./command_line");

command_line.add_command({
    command:"key",
    smallCommand:"k",
    describe:"Input the key",
    demandOption:true,
    type:'number',
    handler: function(){
        console.log("Key");
    }
})


command_line.add_command({
    command:"name",
    smallCommand: "n",
    describe:"Input the name",
    demandOption:true,
    type:"string",
    handler: function(){
        console.log("name");
    }
})

command_line.add_command({
    command:"local",
    smallCommand: "l",
    describe:"Set local",
    ExclusiveIndex: 1,
    handler: function(){
        console.log("local");
    }
})


command_line.add_command({
    command:"remote",
    smallCommand: "r",
    describe:"Set remote",
    ExclusiveIndex: 1,
    handler: function(){
        console.log("remote");
    }
})



command_line.execute();

command_line.display();