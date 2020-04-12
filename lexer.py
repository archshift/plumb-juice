import re

from typing import Iterator, Tuple

tokens = [
    r"[ \n\t]+" # whitespace
    r"\/\/[^\n]*", # comment
    r"(?P<integer>(?:0x[a-fA-F0-9]+|0b[01]+|[0-9]+)[luLU]*)",
    r"(?P<word>[_a-zA-Z0-9]+)",
    r"(?P<delimiter>[,?:;])",
    r"(?P<bracket>[\(\){}\[\]])",
    r"(?P<string>\"(?:[^\\]|\\.)*?\")",
    r"(?P<char>'(?:[^\\]|\\.)')",
    r"(?P<operator>->|<<|>>|&&|\|\||\+\+|--|[.~!=+\-*\/%&^|]=?)",
]

tokenizer = re.compile("|".join(tokens))

Token = Tuple[str, str]
TokenStream = Iterator[Token]

def first_item(d):
    for it in d.items():
        return it
    return None

def tokenize(file: str, input: str) -> Iterator[Tuple[str, str]]:
    for match in tokenizer.finditer(input):
        token_set = { k: v for k, v in match.groupdict().items() if v is not None }
        if len(token_set) > 1:
            print(f"[{file}:{match.pos}] Found ambiguous input token `{match.string}`!")
            exit(-1)
        
        if pair := first_item(token_set):
            yield pair
