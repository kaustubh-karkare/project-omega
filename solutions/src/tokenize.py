from collections import namedtuple
from enum import Enum


TOKENS = Enum(
    'tokens',
    """ASTERISK
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
    PLUS
    QUESTION_MARK
    """
)


Token = namedtuple('token', ['name', 'value'])


def tokenizer(pattern):
    tokens = []
    data_length = len(pattern)
    index = 0
    while index < data_length:
        token_name = None
        if pattern[index] == '*':
            token_name = TOKENS.ASTERISK.name
        elif pattern[index] == '^':
            token_name = TOKENS.CARET.name
        elif pattern[index] == '}':
            token_name = TOKENS.CLOSING_BRACE.name
        elif pattern[index] == ']':
            token_name = TOKENS.CLOSING_BRACKET.name
        elif pattern[index] == ')':
            token_name = TOKENS.CLOSING_PARENTHESIS.name
        elif pattern[index] == ',':
            token_name = TOKENS.COMMA.name
        elif pattern[index] == '$':
            token_name = TOKENS.DOLLAR.name
        elif pattern[index] == '.':
            token_name = TOKENS.DOT.name
        elif pattern[index] == '{':
            token_name = TOKENS.OPENING_BRACE.name
        elif pattern[index] == '[':
            token_name = TOKENS.OPENING_BRACKET.name
        elif pattern[index] == '(':
            token_name = TOKENS.OPENING_PARENTHESIS.name
        elif pattern[index] == '+':
            token_name = TOKENS.PLUS.name
        elif pattern[index] == '?':
            token_name = TOKENS.QUESTION_MARK.name
        elif pattern[index] == '-':
            token_name = TOKENS.MINUS.name
        elif pattern[index] == '\\':
            token_name = TOKENS.ESCAPE_SEQUENCE.name
        elif pattern[index] >= '0' and pattern[index] <= '9':
            token_name = TOKENS.DIGIT.name
        else:
            token_name = TOKENS.LITERAL.name
        tokens.append(Token(name=token_name, value=pattern[index]))
        index += 1
    return tokens
