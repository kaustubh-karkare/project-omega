var command_line=require("./command_line");

command_line.command({
    command:"key",
    describe:"Input the key",
    demandOption:true,
    type:'number',
    handler: function(){
        console.log("Key");
    }
})

command_line.command({
    command:"name",
    describe:"Input the name",
    demandOption:true,
    type:"string",
    handler: function(){
        console.log("name");
    }
})

command_line.command({
    command:"local",
    describe:"Set local",
    ExclusiveIndex: 1,
    handler: function(){
        console.log("local");
    }
})

command_line.command({
    command:"remote",
    describe:"Set remote",
    ExclusiveIndex: 1,
    handler: function(){
        console.log("remote");
    }
})



command_line.execute();

command_line.display();