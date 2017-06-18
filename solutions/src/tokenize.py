from enum import Enum


TOKENS = Enum(
    'tokens',
    """asterisk
    caret
    closing_brace
    closing_bracket
    closing_parenthesis
    digit
    dollar
    dot
    escape_sequence
    literal
    minus
    opening_brace
    opening_bracket
    opening_parenthesis
    plus
    question_mark
    """
)


def tokenizer(pattern):
    tokens = []
    data_length = len(pattern)
    index = 0
    while index < data_length:
        token_name = None
        if pattern[index] == '*':
            token_name = TOKENS.asterisk.name
        elif pattern[index] == '^':
            token_name = TOKENS.caret.name
        elif pattern[index] == '}':
            token_name = TOKENS.closing_brace.name
        elif pattern[index] == ']':
            token_name = TOKENS.closing_bracket.name
        elif pattern[index] == ')':
            token_name = TOKENS.closing_parenthesis.name
        elif pattern[index] == '$':
            token_name = TOKENS.dollar.name
        elif pattern[index] == '.':
            token_name = TOKENS.dot.name
        elif pattern[index] == '{':
            token_name = TOKENS.opening_brace.name
        elif pattern[index] == '[':
            token_name = TOKENS.opening_bracket.name
        elif pattern[index] == '(':
            token_name = TOKENS.opening_parenthesis.name
        elif pattern[index] == '+':
            token_name = TOKENS.plus.name
        elif pattern[index] == '?':
            token_name = TOKENS.question_mark.name
        elif pattern[index] == '-':
            token_name = TOKENS.minus.name
        elif pattern[index] == '\\':
            token_name = TOKENS.escape_sequence.name
        elif pattern[index] >= '0' and pattern[index] <= '9':
            token_name = TOKENS.digit.name
        else:
            token_name = TOKENS.literal.name
        tokens.append((token_name, pattern[index]))
        index += 1
    return tokens
