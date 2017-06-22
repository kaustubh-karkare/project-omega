from tokenize import tokenizer
from regexparser import RegexParser


def check(pattern, text):
    pattern_tokens = tokenizer(pattern)
    source_node = RegexParser(pattern_tokens).parse_regex()
    if source_node.match(text, 0):
        return True
    for ii in range(1, len(text)):
        if source_node.match(text, ii):
            return True
    return False
