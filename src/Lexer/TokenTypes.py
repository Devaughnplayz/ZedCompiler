class TokenType:
    Op = "Operator"
    Sym = "Symbol"
    Float = "Float_Literal"
    Int = "Integer_Literal"
    Str = "String_Literal"
    Key = "Keyword"
    Iden = "Identifier"
    Data = "Datatype"
    char = "Character_Literal"
    EOF = "EOF"
    Bool = "Boolean"

TypeKey  = {
    "import":TokenType.Key,
    "func":TokenType.Key,
    "println":TokenType.Key,
    "input":TokenType.Key,
    "define":TokenType.Key,
    "exit":TokenType.Key,
    "return":TokenType.Key,
    "if":TokenType.Key,
    "else":TokenType.Key,
    "elif":TokenType.Key,
    "while":TokenType.Key,
    "true":TokenType.Bool,
    "false":TokenType.Bool,
    "Null":TokenType.Bool,
    "int":TokenType.Data,
    "void":TokenType.Data,
    "str":TokenType.Data,
    "auto":TokenType.Data,
    "any":TokenType.Data,
    "const":TokenType.Data,
    "float":TokenType.Data,
    "null":TokenType.Bool,
}