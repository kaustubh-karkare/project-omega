#!/usr/bin/ruby

require 'rubygems'
require 'json'

class Argument
	def initialize(full_name,short_form)
		@name = full_name
		@abbrev = short_form
	end
end

arguments = []		#array of predefined arguments
arguments << Argument.new("--key" , "-k") << Argument.new("--name" , "-n") << Argument.new("--local" , "-l") << Argument.new("--remote" , "-r") 
arguments << Argument.new("verbose" , "-v") << Argument.new("help" , "h")

def correct_value(value)
	begin
		val = Interger(value)
		if(val<=0)
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

input_array = ARGV		#array stores the entered arguments
argument_number = input_array.length  	#stores number of arguments
predefined_argumnents = arguments.length 	#stores number of predefined arguments

for i in 0..argument_number-1
	if(input_array.at(i).match(/^--/))   #argument starts with "--" hence using the full name
		match_found = false  #checks if the entered argument is present in the list of predefined arguments
		for j in 0..predefined_argumnents-1
			if(input_array.at(i) == arguments.at(j).name)
				match_found = true
				value = input_array.at(i+1)
				if(j == 0)
					check = correct_value value		#checks if value is a positive integer or not
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
	elsif(input_array.at(i).match(/^-/))   	#argument starts with "-" hence using the abbreviation
		match_found = false  #checks if the entered argument is present in the list of predefined arguments
		for j in 0..predefined_argumnents-1
			if(input_array.at(i) == arguments.at(j).abbrev)
				match_found = true
				value = input_array.at(i+1)
				if(j == 0)
					check = correct_value value		#checks if value is a positive integer or not
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
				if(j == 4)
					puts json.dumps({'command': input_array.at(i-2), 'sub-command': input_array.at(i-1), 'Verbose':'true'})
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
	
