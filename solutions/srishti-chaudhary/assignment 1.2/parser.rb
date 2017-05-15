#!/usr/bin/ruby

require 'rubygems'
require 'json'

json_object = {}
class Argument
	def initialize (full_name , pos)
		@name = full_name
		@positional = pos
	end
end

arguments = []		# array of predefined arguments

def argument_builder(full_name , postional = "false")
	arguments<<Argument.new(full_name , postional)	
end

def correct_value (value)
	begin
		val = Integer (value)
		if (val<=0)
			puts "Value for key must be a positive integer"
			return false
		end
		return true
	rescue
		puts "Value for key must be a positive integer"
		return false
	end
end

def display_help
	puts "Help:"
	puts "--key: positive integer"
	puts "--name: string"
	puts "--local and remote should not be together"
end
def parser
	for i in 0..argument_number-1
		if (input_array.at(i).match(/^--/))   # argument starts with "--" 
			match_found = false  		# checks if the entered argument is present in the list of predefined arguments
			for j in 0..predefined_argumnents-1
				if(input_array.at(i) == arguments.at(j).name)
					match_found = true
					value = input_array.at(i+1)
					if(j == 0)
						check = correct_value value		# checks if value is a positive integer or not
						if(check == true)
							puts json.dumps({'key': input_array.at(i), 'value': input_array.at(i+1)})
						end
					end
					if(j == 2)
						flag = false
						for k in i+1..argument_number-1
							if(input_array.at(i) == "--remote")
								puts "Error: --local and --remote arguments cannot be used together"
								flag = true
							end
						end
						if(flag == false)
							puts json.dumps({'local': 'true'})
						end
					end
					if(j == 3)
						flag = false
						for k in i+1..argument_number-1
							if(input_array.at(i) == "--local")
								puts "Error: --local and --remote arguments cannot be used together"
								flag = true
							end
						end
						if(flag == false)
							puts json.dumps({'remote': 'true'})
						end
					end
					if(j == 5)
						display_help
					end
					if(match_found == false)
						puts "Invalid argument"
					end
				end
			end
		end
	end
end

argument_builder "--key" 
argument_builder "--name"
argument_builder "--local" 
argument_builder "--remote"
argument_builder "verbose"
argument_builder "help" 
argument_builder "command" "true"
argument_builder "subcommand" "true" 

input_array = ARGV		# array stores the entered arguments
argument_number = input_array.length  	# stores number of arguments
predefined_argumnents = arguments.length 	# stores number of predefined arguments	

parser
