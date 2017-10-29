class VCSError < Exception

    def initialize(message = nil)
        super(message)
    end

end


class ObjectFileError < VCSError

    # The exception indicates that the object file may be missing or may have
    # been corrupt or the data format(type of object) is not acceptable.
end


class MissingConfigParameter < VCSError

    # The exception indicates that the config file does not 
    # contain the argument queried for.
end


class NotVCSRepository < VCSError

    # The exception indicates that directory has not been initialized or
    # is missing files within the .vcs directory.
end


class MissingCommitParameter < VCSError

    # The exception indicates that the commit was missing message.
end
