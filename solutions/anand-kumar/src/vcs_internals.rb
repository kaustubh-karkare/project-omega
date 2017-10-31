require 'json'
require './exceptions'


class VCS

    attr_reader :vcs, :objects, :config

    def initialize(directory = Dir.getwd())
        # Initialize paths in the directory
        @vcs = File.join(directory, ".vcs")
        @objects = File.join(@vcs, "objects")
        @config = File.join(@vcs, "config")
    end

    def get_option(config_key)
        # The method returns the the config parameter value.

        config_parameters = {}
        File.open(@config, "rb") do |config_file|
            config_parameters = JSON.load(config_file)
        end
        if config_parameters.include? (config_key)
            return config_parameters.fetch(config_key)
        else
            raise MissingConfigParameter.new("#{config_key} not found")
        end
    end

    def set_option(config_key, config_value)
        # The method adds/updates the config file parameters.

        config_parameters = Hash.new()
        File.open(@config, "rb") do |config_file|
            config_parameters = JSON.load(config_file)
        end
        if config_parameters.nil?
            # File has not been initialized.
            config_parameters = Hash.new()
        end
        config_parameters[config_key] = config_value
        File.open(@config, "wb") do |config_file|
            JSON.dump(config_parameters, config_file)
        end
    end
end
