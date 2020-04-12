import lexer

from typing import List, Tuple, Optional, Set, Deque
from collections import deque

modifier_keywords = {
    "static", "const", "inline", "register", "volatile"
}
int_keywords = {
    "char", "byte", "short", "int", "long"
}
type_keywords = int_keywords | {
    "struct", "union", "enum",
    "void", "unsigned", "float", "double"
}
control_keywords = {
    "switch", "case", "return", "break", "for", "while", "if", "else", "do", "goto"
}


class Type:
    POINTER = "pointer"
    VALUE = "value"
    FUNCPTR = "funcptr"
    ARRAY = "array"

    storage = None
    pointee = None
    val = None
    outty = None
    paramtys = None
    size = None

    @staticmethod
    def pointer(pointee):
        t = Type()
        t.storage = Type.POINTER
        t.pointee = pointee
        return t

    @staticmethod
    def value(what: List[str]):
        t = Type()
        t.storage = Type.VALUE
        t.val = what
        return t

    @staticmethod
    def funcptr(outty, paramtys: List):
        t = Type()
        t.storage = Type.FUNCPTR
        t.outty = outty
        t.paramtys = paramtys
        return t
    
    @staticmethod
    def array(pointee, size):
        t = Type()
        t.storage = Type.ARRAY
        t.pointee = pointee
        t.size = size
        return t
    
    def __str__(self):
        if self.storage == self.POINTER:
            return f"Type *{{{self.pointee}}}"
        elif self.storage == self.VALUE:
            val = " ".join(map(str, self.val))
            return f"Type {{{val}}}"
        elif self.storage == self.FUNCPTR:
            return f"Type fn({self.paramtys}) -> {{{self.outty}}})"
        elif self.storage == self.ARRAY:
            return f"Type {{{self.pointee}}}[{self.size}]"



class FunctionParam:
    def __init__(self, ty: Type, name: Optional[str] = None):
        self.ty = ty
        self.name = name
    
    def __str__(self):
        return f"Param {self.name}: {self.ty}"



class Definition:
    FUNCTION = "function"
    VALUE = "value"

    storage = None
    name = None
    outty = None
    paramtys = None
    body = None
    ty = None
    val = None

    @staticmethod
    def function(name: Optional[str], outty: Type, paramtys: List[FunctionParam], body: List['Statement']):
        d = Definition()
        d.storage = Definition.FUNCTION
        d.name = name
        d.outty = outty
        d.paramtys = paramtys
        d.body = body
        return d

    @staticmethod
    def value(name: Optional[str], ty: Type, value: 'Expression'):
        d = Definition()
        d.storage = Definition.VALUE
        d.name = name
        d.ty = ty
        d.val = value
        return d

    def __str__(self):
        if self.storage == self.VALUE:
            if self.val is not None:
                return f"Define {self.name}: {{{self.ty}}} = {self.val}"
            return f"Declare {self.name}: {{{self.ty}}}"

        elif self.storage == self.FUNCTION:
            params = ", ".join( map(str, self.paramtys) )
            if self.body is not None:
                body = "\n".join(map("    {}".format, self.body))
                return f"Define fn {self.name}({params}) -> {{{self.outty}}}\n{{\n{body}\n}}"
            return f"Declare fn {self.name}({params}) -> {{{self.outty}}}"




class Expression:
    STRING = "string"
    INTEGER = "integer"
    PREFIX = "prefix"
    POSTFIX = "postfix"
    DECONSTRUCT = "deconstruct"
    INDEX = "index"
    VARIABLE = "variable"
    INFIX = "infix"

    storage = None
    ty = None
    strval = None
    intval = None
    op = None
    exp1 = None
    exp2 = None
    varname = None
    ident = None

    @staticmethod
    def variable(name: str):
        e = Expression()
        e.storage = Expression.VARIABLE
        e.varname = name
        return e

    @staticmethod
    def char(literal: str):
        e = Expression()
        e.storage = Expression.INTEGER
        e.ty = Type.value(["char"])
        e.intval = ord(eval(literal))
        return e

    @staticmethod
    def string(literal: str):
        e = Expression()
        e.storage = Expression.STRING
        e.strval = eval(literal)
        return e

    @staticmethod
    def integer(literal: str):
        e = Expression()
        e.storage = Expression.INTEGER
        e.ty = Type.value(["int"])
        if literal.startswith("0x"):
            e.intval = int(literal[2:], base=16)
        elif literal.startswith("0b"):
            e.intval = int(literal[2:], base=2)
        elif literal.startswith("0") and literal != "0":
            e.intval = int(literal[1:], base=8)
        else:
            e.intval = int(literal)
        return e
    
    @staticmethod
    def prefix(op: str, val: 'Expression'):
        e = Expression()
        e.storage = Expression.PREFIX
        e.exp1 = val
        e.op = op
        return e

    @staticmethod
    def postfix(op: str, val: 'Expression'):
        e = Expression()
        e.storage = Expression.POSTFIX
        e.exp1 = val
        e.op = op
        return e

    @staticmethod
    def infix(op1: 'Expression', op: str, op2: 'Expression'):
        e = Expression()
        e.storage = Expression.INFIX
        e.exp1 = op1
        e.exp2 = op2
        e.op = op
        return e

    @staticmethod
    def index(val: 'Expression', index: 'Expression'):
        e = Expression()
        e.storage = Expression.INDEX
        e.exp1 = val
        e.exp2 = index
        return e

    @staticmethod
    def deconstruct(val: 'Expression', op: str, ident: str):
        e = Expression()
        e.storage = Expression.DECONSTRUCT
        e.exp1 = val
        e.op = op
        e.ident = ident
        return e
    
    def __str__(self):
        if self.storage == self.VARIABLE:
            return f"(Var {self.varname})"
        elif self.storage == self.INTEGER:
            return f"({self.ty} {self.intval})"
        elif self.storage == self.STRING:
            return f"\"{self.strval}\""
        elif self.storage == self.PREFIX:
            return f"({self.op} {self.exp1})"
        elif self.storage == self.POSTFIX:
            return f"({self.exp1} {self.op})"
        elif self.storage == self.INFIX:
            return f"({self.exp1} {self.op} {self.exp2})"
        elif self.storage == self.DECONSTRUCT:
            return f"({self.exp1} {self.op} {self.ident})"
        elif self.storage == self.INDEX:
            return f"({self.exp1} [ {self.exp2} ])"




class Statement:
    EXPRESSION = "expression"
    DEFINITION = "definition"
    RETURN = "return"
    GOTO = "goto"
    BREAK = "break"

    storage = None
    val = None
    defn = None
    ident = None

    @staticmethod
    def expression(expr: Expression):
        s = Statement()
        s.storage = Statement.EXPRESSION
        s.val = expr
        return s

    @staticmethod
    def definition(defn: Definition):
        s = Statement()
        s.storage = Statement.DEFINITION
        s.defn = defn
        return s
    
    @staticmethod
    def ret(val: Expression):
        s = Statement()
        s.storage = Statement.RETURN
        s.val = val
        return s

    @staticmethod
    def goto(ident: str):
        s = Statement()
        s.storage = Statement.GOTO
        s.ident = ident
        return s

    @staticmethod
    def brk():
        s = Statement()
        s.storage = Statement.BREAK
        return s
    
    def __str__(self):
        if self.storage == self.DEFINITION:
            return str(self.defn)
        elif self.storage == self.EXPRESSION:
            return f"Apply {self.val}"
        elif self.storage == self.RETURN:
            return f"Return {self.val}"




def parse_toplevel(tokstr: lexer.TokenStream):
    taken: Deque[lexer.Token] = deque()

    def take() -> lexer.Token:
        nonlocal taken
        if not len(taken):
            out = next(tokstr)
        else:
            out = taken.popleft()
        return out

    def peek(n = None) -> lexer.Token:
        nonlocal taken

        deref = n is None
        n = n or 1
        
        while len(taken) < n:
            taken.append(next(tokstr))
        
        if deref:
            return taken[0]
        else:
            return list(taken)[:n]
    
    def done():
        try:
            peek(1)
            return False
        except StopIteration:
            return True

    def expect(ty: str, val: str = None, vset = None, check: bool = False) -> Optional[str]:
        tok = peek()
        if val is not None and tok[1] != val:
            if check:
                print(f"Expected token `{val}`, got {tok[1]}!")
                exit(-1)
            return None
        if vset is not None and tok[1] not in vset:
            if check:
                print(f"Expected one of `{', '.join(vset)}`, got {tok[1]}!")
                exit(-1)
            return None
        if tok[0] != ty:
            if check:
                print(f"Expected token of type `{ty}`, got {tok[0]} `{tok[1]}`!")
                exit(-1)
            return None

        tok = take()
        return tok[1]
    
    def take_modifiers() -> List[str]:
        modifiers: List[str] = []
        while True:
            mod = expect("word", vset=modifier_keywords)
            if not mod:
                return modifiers
            modifiers.append(mod)
    
    def take_funcptr() -> Optional[Tuple[Optional[str], List[Type]]]:
        if not expect("bracket", "("):
            return None
        
        expect("operator", "*", check=True)
        name = expect("word")
        expect("bracket", "(", check=True)
        expect("bracket", ")", check=True)
        expect("bracket", ")", check=True)

        # TODO: function pointer args, array pointers

        return name, []
    
    def expect_expression_unary() -> Expression:
        op_stack = []
        while op := expect("operator", vset={"++", "--", "~", "!", "*", "-", "+", "&"}):
            op_stack.append(op)
        
        if expect("bracket", "("):
            val = expect_expression()
            expect("bracket", ")", check=True)
        
        elif i := expect("integer"):
            val = Expression.integer(i)
        
        elif s := expect("string"):
            val = Expression.string(s)

        elif c := expect("char"):
            val = Expression.char(c)

        elif n := expect("word"):
            val = Expression.variable(n)

        else:
            assert(not "unimplemented")
        
        while op := expect("operator", vset={"++", "--", ".", "->"}) or expect("bracket", vset={"[", "("}):
            if op in {"++", "--"}:
                val = Expression.postfix(op, val)
            elif op in {".", "->"}:
                ident = expect("word", check=True)
                val = Expression.deconstruct(val, op, ident)
            elif op == "[":
                index = expect_expression()
                expect("bracket", "]", check=True)
                val = Expression.index(val, index)

        while len(op_stack):
            op = op_stack.pop()
            val = Expression.prefix(op, val)
        return val
    
    def expect_expression_inner(opstack: List[Set[str]]):
        if not len(opstack):
            return expect_expression_unary()

        top_set = opstack[-1]
        rest_set = opstack[:-1]
        
        val = expect_expression_inner(rest_set)
        while op := expect("operator", vset=top_set):
            op2 = expect_expression_inner(rest_set)
            val = Expression.infix(val, op, op2)
        
        return val

    def expect_expression():
        return expect_expression_inner([
            {"*", "/", "%"},
            {"+", "-"},
            {"<<", ">>"},
            {"<", "<=", ">=", ">"},
            {"==", "!="},
            {"&"},
            {"^"},
            {"|"},
            {"&&"},
            {"||"},
            {"=", "+=", "-=", "*=", "/=", "%=", "<<=", ">>=", "&=", "^=", "|="}
        ])
        # TODO: ternary, comma
    

    
    def expect_type() -> Tuple[Type, Optional[str]]:
        typeparts = []
        
        if tw := expect("word", val="unsigned"):
            typeparts.append(tw)
            if tw := expect("word", val="long"):
                typeparts.append(tw)
                if tw := expect("word", vset={"long", "int"}):
                    typeparts.append(tw)
    
        elif tw := expect("word", val="long"):
            typeparts.append(tw)
            if tw := expect("word", vset={"long", "int", "double"}):
                typeparts.append(tw)
        
        elif tw := expect("word", vset={"struct", "union"}):
            typeparts.append(tw)
            tw = expect("word", check=True)
            typeparts.append(tw)
        
        elif tw := expect("word", check=True):
            typeparts.append(tw)
        
        basety = Type.value(typeparts)

        while expect("operator", "*"):
            basety = Type.pointer(basety)

        funcptr = take_funcptr()
        if funcptr is not None:
            name, args = funcptr
            basety = Type.funcptr(basety, args)
        else:
            name = expect("word")

        if expect("bracket", "["):
            expr = None
            if not expect("bracket", "]"):
                expr = expect_expression()
                expect("bracket", "]", check=True)
            basety = Type.array(basety, expr)

        return basety, name
    

    def expect_definition() -> Definition:
        mods = take_modifiers()
        ty, name = expect_type()
        val = None

        if expect("bracket", "("):
            paramtys = []

            if not expect("bracket", ")"):
                paramtys.append(FunctionParam(*expect_type()))
                while expect("delimiter", ","):
                    paramtys.append(FunctionParam(*expect_type()))
                expect("bracket", ")", check=True)
            
            if expect("bracket", "{"):
                body = expect_body()
                return Definition.function(name, ty, paramtys, body)
            
            else:
                expect("delimiter", ";", check=True)
                return Definition.function(name, ty, paramtys, None)

        elif expect("operator", "="):
            val = expect_expression()
        
        expect("delimiter", ";", check=True)
        return Definition.value(name, ty, val)
    
    
    def take_control_statement():
        keyword = expect("word", vset=control_keywords)
        if not keyword:
            return None
        
        if keyword == "return":
            exp = expect_expression()        
            expect("delimiter", ";")
            return Statement.ret(exp)
        elif keyword == "break":
            expect("delimiter", ";")
            return Statement.brk()
        elif keyword == "goto":
            ident = expect("word", check=True)
            expect("delimiter", ";")
            return Statement.goto(ident)
        else:
            assert(not "unimplemented")
    

    def expect_statement():
        if control := take_control_statement():
            return control

        if mods := take_modifiers():
            # Variable declaration and assignment
            defn = expect_definition()
            return Statement.definition(defn)
        
        w1, w2 = peek(n=2)
        if w1[0] == "word" and w2[0] == "word":
            # Variable declaration and assignment
            defn = expect_definition()
            return Statement.definition(defn)
        
        expr = expect_expression()
        expect("delimiter", ";", check=True)
        return Statement.expression(expr)

    
    def expect_body():
        stmts = []
        while not expect("bracket", "}"):
            if stmt := expect_statement():
                stmts.append(stmt)
        return stmts
    
    defns = []
    while not done():
        defns.append(expect_definition())
    return defns
    

file = "test.c"
with open(file) as input:
    input = input.read()
    tokstr = lexer.tokenize(file, input)
    ast = parse_toplevel(tokstr)
    print("\n".join(map(str, ast)))

