from src.Lexer.TokenTypes import TokenType, TypeKey
from colorama import Fore, Style
import colorama
colorama.init(autoreset=True)
import sys

class Lexer:
    def __init__(self, FileName, SourceCode):
        self.FileName = FileName
        self.SourceCode = SourceCode
        self.SourceLines = SourceCode.split('\n')

    def Index(self, Pos):
        try:
            self.SourceCode[Pos]
        except:
            return ""
        else:
            return self.SourceCode[Pos]

    def Lexer(self):
        ErrorCount = 0
        Tokens = []
        Pos = 0
        Coloum = 1
        Line = 1

        def push(Type, Value, Coloum, Line):
            Tokens.append({"Type":Type, "Value":Value, "Coloum":Coloum, "Line":Line})


        while Pos < len(self.SourceCode):
            Peek  = self.Index(Pos + 1)
            Peek_Plus = self.Index(Pos + 2)
            match(self.Index(Pos)):
                case '\n':
                    Coloum = 0
                    Line+=1
                case "":
                    pass
                case " ":
                    pass
                case "+":
                    if Peek == "+":
                        push(TokenType.Op, "++", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    elif Peek == "=":
                        push(TokenType.Op, "+=", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    else:
                        push(TokenType.Op, "+", Coloum, Line)
                case "*":
                    if Peek == "=":
                        push(TokenType.Op, "*=", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    else:
                        push(TokenType.Op, "*", Coloum, Line)
                case "/":        
                    if Peek == "/":
                        while self.Index(Pos) != '\n':
                            Pos+=1
                        Coloum = 0
                        Line+=1
                    elif Peek == "*":
                        Pos+=2
                        while self.Index(Pos) != "*" and self.Index(Pos + 1) != "/":
                            if(self.Index(Pos) == '\n'):
                                Line+=1
                                Coloum = 0
                            Pos+=1
                            Coloum+=1
                        Pos+=1
                        Coloum+=1
                    elif Peek == "=":
                        push(TokenType.Op, "/=", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    else:
                        push(TokenType.Op, "/", Coloum, Line)
                case "-":
                    if Peek == "-":
                        push(TokenType.Op, "--", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    elif Peek == "=":
                        push(TokenType.Op, "-=", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    elif Peek.isdigit():
                        Number = "-"
                        DotCount = 0
                        Pos+=1
                        Coloum+=1
                        while Pos < len(self.SourceCode) and self.Index(Pos).isdigit() or self.Index(Pos) == ".":
                            if self.Index(Pos) == ".":
                                DotCount+=1
                            if DotCount > 1:
                                break
                            Number+=self.Index(Pos)
                            Pos+=1
                            Coloum+=1
                        Pos-=1
                        Coloum-=1
                        if DotCount > 0:
                            push(TokenType.Float, Number, Coloum, Line)
                        else:
                            push(TokenType.Int, Number, Coloum, Line)
                    else:
                        push(TokenType.Op, "-", Coloum, Line)
                case "=":
                    if Peek == "=":
                        push(TokenType.Op, "==", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    else:
                        push(TokenType.Op, "=", Coloum, Line)
                case "%":
                    if Peek == "=":
                        push(TokenType.Op, "%=", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    else:
                        push(TokenType.Op, "%", Coloum, Line)
                case "&":
                    if Peek == "&":
                        push(TokenType.Op, "&&", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    elif Peek == "=":
                        push(TokenType.Op, "&=", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    else:
                        push(TokenType.Op, "&", Coloum, Line)
                case "|":
                    if Peek == "|":
                        push(TokenType.Op, "||", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    elif Peek == "=":
                        push(TokenType.Op, "!=", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    
                    else:
                        push(TokenType.Op, "|", Coloum, Line)
                case "^":
                    if Peek == "=":
                        push(TokenType.Op, "^", Coloum, Line)
                case "~":
                    push(TokenType.Op, "~", Coloum, Line)
                case "<":
                    if Peek == "<" and Peek_Plus != "=":
                        push(TokenType.Op, "<<", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    elif Peek == "<" and Peek_Plus == "=":
                        push(TokenType.Op, "<<=", Coloum, Line)
                        Pos+=2
                        Coloum+=2
                    elif Peek == "=":
                        push(TokenType.Op, "<=", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    else:
                        push(TokenType.Op, "<", Coloum, Line)
                case ">":
                    if Peek == ">" and Peek_Plus != "=":
                        push(TokenType.Op, ">>", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    elif Peek == ">" and Peek_Plus == "=":
                        push(TokenType.Op, ">>=", Coloum, Line)
                        Pos+=2
                        Coloum+=2
                    elif Peek == "=":
                        push(TokenType.Op, ">=", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    else:
                        push(TokenType.Op, ">", Coloum, Line)
                case ":":
                    if Peek == ":":
                        push(TokenType.Op, "::", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    else:
                        push(TokenType.Op, ":", Coloum, Line)
                case "?":
                    push(TokenType.Op, "?", Coloum, Line)
                case "!":
                    if Peek == "=":
                        push(TokenType.Op, "!=", Coloum, Line)
                        Pos+=1
                        Coloum+=1
                    else:
                        push(TokenType.Op, "!", Coloum, Line)
                
                case ".":
                    push(TokenType.Op, ".", Coloum, Line)

                case "(":
                    push(TokenType.Sym, "(", Coloum, Line)
                
                case ")":
                    push(TokenType.Sym, ")", Coloum, Line)
                
                case "{":
                    push(TokenType.Sym, "{", Coloum, Line)
                
                case "}":
                    push(TokenType.Sym, "}", Coloum, Line)

                case "[":
                    push(TokenType.Sym, "[", Coloum, Line)
            
                case "]":
                    push(TokenType.Sym, "]", Coloum, Line)
                
                case ";":
                    push(TokenType.Sym, ";", Coloum, Line)

                case ",":
                    push(TokenType.Sym, ",", Coloum, Line)
                
                case _:
                    if self.Index(Pos).isdigit():
                        Number = ""
                        DotCount = 0
                        Startc = Coloum
                        while Pos < len(self.SourceCode) and self.Index(Pos).isdigit() or self.Index(Pos) == ".":
                            if self.Index(Pos) == ".":
                                DotCount+=1
                            if DotCount > 1:
                                break
                            Number+=self.Index(Pos)
                            Pos+=1
                            Coloum+=1
                        Pos-=1
                        Coloum-=1
                        if DotCount > 0:
                            push(TokenType.Float, Number, Startc, Line)
                        else:
                            push(TokenType.Int, Number, Startc, Line)
                    elif self.Index(Pos).isalpha() or self.Index(Pos) == "_":
                        KeyWord_or = ""
                        Startc = Coloum
                        while Pos < len(self.SourceCode) and self.Index(Pos).isalpha() or self.Index(Pos) == "_" or self.Index(Pos).isdigit():
                            KeyWord_or+=self.Index(Pos)
                            Pos+=1
                            Coloum+=1
                        Pos-=1
                        Coloum-=1

                        if TypeKey.get(KeyWord_or, None) != None:
                            push(TypeKey.get(KeyWord_or, None), KeyWord_or, Startc, Line)
                        else:
                            push(TokenType.Iden, KeyWord_or, Startc, Line)
                    elif self.Index(Pos) == '"':
                        String = "\""
                        Startc = Coloum
                        Pos+=1
                        Coloum+=1
                        Reset = False
                        while Pos < len(self.SourceCode):
                            if self.Index(Pos) == '\n':
                                print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Fore.RED}SyntaxError:{Fore.RESET} Unterminated string (\") ", file=sys.stderr)
                                print(f"{Line}|{self.SourceLines[Line - 1]}", file=sys.stderr)
                                print(f"{len(str(Line)) * " "}|{(len(String) - Coloum) * " "}{Fore.RED}^{(len(String) - 1) * "~"}^", file=sys.stderr)
                                print(f"{len(str(Line)) * " "}|{(len(String) - Coloum) * " "}{(len(String)) * " "}{Fore.BLUE}{Style.BRIGHT}\"", file=sys.stderr)
                                ErrorCount+=1
                                Reset = True
                                break
                            if self.Index(Pos) == '"' and self.Index(Pos - 1) != "\\":
                                String+="\""
                                break
                            String+=self.Index(Pos)
                            Pos+=1
                            Coloum+=1

                        if Reset == True:
                            Line+=1
                            Coloum = 0
                        push(TokenType.Str, String, Startc, Line)
                    elif self.Index(Pos) == "'":
                        Charcter = "'"
                        Startc = Coloum
                        Pos+=1
                        Coloum+=1
                        Reset = False
                        while Pos < len(self.SourceCode):
                            if self.Index(Pos) == '\n':
                                print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Fore.RED}SyntaxError:{Fore.RESET} Unterminated chracter (') ", file=sys.stderr)
                                print(f"{Line}|{self.SourceLines[Line - 1]}", file=sys.stderr)
                                print(f"{len(str(Line)) * " "}|{(len(Charcter) - Coloum) * " "}{Fore.RED}^{(len(Charcter) - 1) * "~"}^", file=sys.stderr)
                                print(f"{len(str(Line)) * " "}|{(len(Charcter) - Coloum) * " "}{(len(Charcter)) * " "}{Fore.BLUE}{Style.BRIGHT}'", file=sys.stderr)
                                ErrorCount+=1
                                Reset = True
                                break
                            if self.Index(Pos) == "'":
                                Charcter+="'"
                                break
                            Charcter+=self.Index(Pos)
                            Pos+=1
                            Coloum+=1
                        if len(Charcter) > 3:
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Fore.MAGENTA}Warning:{Fore.RESET} Multi-character character(char) constant{Style.RESET_ALL}", file=sys.stderr)
                            print(f"{Line}|{self.SourceLines[Line - 1]}", file=sys.stderr)
                            print(f"{len(str(Line)) * " "}|{(len(Charcter) - Coloum) * " "}{Fore.MAGENTA}{len(Charcter) * "~"}", file=sys.stderr)
                        
                        if Reset == True:
                            Line+=1
                            Coloum = 0
                        push(TokenType.char, Charcter, Startc, Line)                   
                    else:
                        print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Fore.RED}SyntaxError:{Fore.RESET} Unrecognized token '{self.SourceLines[Line - 1][Coloum - 1]}'{Style.RESET_ALL}", file=sys.stderr)
                        print(f"{Line}|{self.SourceLines[Line - 1]}", file=sys.stderr)
                        print(f"{len(str(Line)) * " "}|{(Coloum - 1) * " "}{Fore.RED}^{Fore.RESET}", file=sys.stderr)
                        ErrorCount+=1
            Pos+=1 
            Coloum+=1
        if ErrorCount > 0:
            exit(1)
        push(TokenType.EOF, "EOF", Coloum, Line)
        return Tokens