from collections import namedtuple
from enum import Enum


TOKENS = Enum(
    'tokens',
    """
    ASTERISK
    CARET
    CLOSING_BRACE
    CLOSING_BRACKET
    CLOSING_PARENTHESIS
    COMMA
    DIGIT
    DOLLAR
    DOT
    ESCAPE_SEQUENCE
    LITERAL
    MINUS
    OPENING_BRACE
    OPENING_BRACKET
    OPENING_PARENTHESIS
    OR
    PLUS
    QUESTION_MARK
    """
)


Token = namedtuple('token', ['type', 'value'])


def tokenizer(pattern):
    tokens = []
    data_length = len(pattern)
    index = 0
    while index < data_length:
        token_type = None
        if pattern[index] == '*':
            token_type = TOKENS.ASTERISK
        elif pattern[index] == '^':
            token_type = TOKENS.CARET
        elif pattern[index] == '}':
            token_type = TOKENS.CLOSING_BRACE
        elif pattern[index] == ']':
            token_type = TOKENS.CLOSING_BRACKET
        elif pattern[index] == ')':
            token_type = TOKENS.CLOSING_PARENTHESIS
        elif pattern[index] == ',':
            token_type = TOKENS.COMMA
        elif pattern[index] == '$':
            token_type = TOKENS.DOLLAR
        elif pattern[index] == '.':
            token_type = TOKENS.DOT
        elif pattern[index] == '{':
            token_type = TOKENS.OPENING_BRACE
        elif pattern[index] == '[':
            token_type = TOKENS.OPENING_BRACKET
        elif pattern[index] == '(':
            token_type = TOKENS.OPENING_PARENTHESIS
        elif pattern[index] == '|':
            token_type = TOKENS.OR
        elif pattern[index] == '+':
            token_type = TOKENS.PLUS
        elif pattern[index] == '?':
            token_type = TOKENS.QUESTION_MARK
        elif pattern[index] == '-':
            token_type = TOKENS.MINUS
        elif pattern[index] == '\\':
            token_type = TOKENS.ESCAPE_SEQUENCE
        elif pattern[index] >= '0' and pattern[index] <= '9':
            token_type = TOKENS.DIGIT
        else:
            token_type = TOKENS.LITERAL
        tokens.append(Token(type=token_type, value=pattern[index]))
        index += 1
    return tokens
