from tokenize import tokenizer
from regexparser import RegexParser


def check(pattern, text):
    pattern_tokens = tokenizer(pattern)
    root_node = RegexParser(pattern_tokens).parse_regex()
    if root_node.match(text, 0):
        return True
    else:
        for ii in range(1, len(text)):
            if root_node.match(text, ii):
                return True
    return False
