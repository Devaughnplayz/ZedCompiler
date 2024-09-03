import sys
import colorama
from colorama import Fore, Style
colorama.init(autoreset=True)

#--Compiler Tools--
#DevNote:: The Compiler parsts like the lexer are needed mailky for file imports
from src.Lexer.Lexer import Lexer
from src.Parser.AstTypes import Program, Satement, Expression, StringOptions
from src.Lexer.TokenTypes import TokenType
from src.Environment.Enivironment import Environment

#---Table For Stuff--
MemoryPointer = {

}


#--Actual Parser--
#Note Never Make A Compiler Again
class Parser:
    def __init__(self, SourceLines, LexedTokens, FileName, Environment, ImportTable=[]):
        self.FileName = FileName
        self.SourceLines = SourceLines
        self.ImportTable = ImportTable
        self.Tokens = LexedTokens
        self.ErrorCount = 0
        self.Environment = Environment
        self.FoundFloat = False
        self.Tokenscount = 0

        #---Tbales--
        self.LinkTable = []

        #Tracked Value
        self.Line = [0]
        self.Coloum = [0]
        self.Coloumend = [0]
        self.EvalImport = False

        self.EnvironmentList = [Environment]
        self.EnvironmentNum = self.Environment.ScopeNum

        self.TypeTransalate = {
            TokenType.Int : "int",
            TokenType.Float : "float",
            TokenType.Str : "str",
            TokenType.char : "char"
        }

        self.ImportTable.append(FileName)

    def At(self):
        return self.Tokens[0]

    def Transalte(self, Type):
        if self.TypeTransalate.get(Type, None) != None:
            return self.TypeTransalate.get(Type, None)
        else:
            return Type

    def not_eof(self):
        return self.Tokens[0].get("Type") != TokenType.EOF
        
    def GetVT(self, Token, Type, Value):
        return Token.get("Type") == Type and Token.get("Value") == Value
    def eat(self):
        if self.At().get("Type") == TokenType.EOF:
            Prev =  self.At()
            self.Line.append(Prev.get("Line"))
            self.Coloum.append(Prev.get("Coloum"))
            self.Coloumend.append(Prev.get("Coloum") + len(Prev.get("Value")))
            return Prev
        
        self.Tokenscount+=1

        Prev = self.At()
        self.Tokens = self.Tokens[1:]
        self.Line.append(Prev.get("Line"))
        self.Coloum.append(Prev.get("Coloum"))
        self.Coloumend.append(Prev.get("Coloum") + len(Prev.get("Value")))
        return Prev
    
    def Expected(self, Type, Value):
        Token = self.eat()
        if self.GetVT(Token, Type, Value) != True:
                Line = self.Line[-2]
                Coloum = self.Coloumend[-2]


                print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}SyntaxError:{Fore.RESET} Expected '{Value}' instead recived '{Token.get("Value")}' ")
                print(f"{Line}|{self.SourceLines[Line - 1]}")
                print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum - 1) * " "}^{Fore.RESET}")
                print(f"{len(str(Line)) * " "}|{Fore.BLUE}{(Coloum - 1) * " "}{Value}{Fore.RESET}")
                self.ErrorCount+=1

        return Token

    def ExpectedType(self, Type, Word):
        Token = self.eat()
        if Token.get("Type") != Type:
                Line = self.Line[-1]
                Coloum = self.Coloum[-1]


                print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}SyntaxError:{Fore.RESET} Expected a {Type} after {Word}")
                print(f"{Line}|{self.SourceLines[Line - 1]}")
                print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum - 1) * " "}{(self.Coloumend[-1] - Coloum)* "^"}{Fore.RESET}")
                self.ErrorCount+=1

        return Token

    def Parser(self):
        Ast = {
            "Type":Program.Prg,
            "File":self.FileName,
            "LinkTable":self.LinkTable,
            "Name":"StartProgram",
            "Body":[],
        }

        while self.not_eof():
            LastEvalNode = self.parse_stmt()
            if self.EvalImport == True:
                for i in LastEvalNode.get("Body"): # type: ignore
                    Ast['Body'].append(i)
                self.EvalImport = False
                self.Line = []
                self.Coloum = []
                self.Coloumend = []
                self.FoundFloat = False
            else:
                Ast['Body'].append(LastEvalNode)
                self.Line = []
                self.Coloum = []
                self.Coloumend = []
                self.FoundFloat = False

        if self.ErrorCount > 0:
            exit(1)
        return Ast


    def parse_stmt(self):
        if self.GetVT(self.At(), TokenType.Key, "exit"):
            return self.parse_exit_stmt()
        elif self.At().get("Type") == TokenType.Data:
            return self.parse_var_dec_stmt()
        elif self.GetVT(self.At(), TokenType.Key, "func"):
            return self.parse_func_dec_stmt()
        elif self.GetVT(self.At(), TokenType.Key, "return"):
            return self.parse_return_stmt()
        elif self.GetVT(self.At(), TokenType.Key, "import"):
            return self.parse_import_stmt()
        elif self.GetVT(self.At(), TokenType.Key, "println"):
            return self.parse_println_stmt()
        elif self.GetVT(self.At(), TokenType.Key, "if"):
            return self.parse_if_stmt()
        elif self.GetVT(self.At(), TokenType.Key, "while"):
            return self.parse_while_stmt()
        else:
            AstNode = self.parse_expr()  
            if AstNode not in []:   
                self.Expected(TokenType.Sym, ";")   
            return AstNode

    def parse_func_dec_stmt(self):
        global GotReturn
        self.eat()
        Name = self.ExpectedType(TokenType.Iden, "func")
        if Name.get("Value") == "main":
            self.Expected(TokenType.Op, ":")
            RetType = self.Expected(TokenType.Data, "int")
            
            self.EnvironmentNum+=1
            self.Environment = Environment(self.Environment, self.EnvironmentNum)
            self.EnvironmentList.append(self.Environment)

            Args = self.parse_args()

            ArgType = {}
            for idex, i in enumerate(Args): # type: ignore
                AType = i.get("VarType") # type: ignore
                ArgType.update({idex:AType})

            Body = []
            Tree = {
                "Type":Program.Main,
                "ReturnType":RetType.get("Value"),
                "Name":Name.get("Value"),
                "Args":Args,
                "Body":Body,
                "ArgTypes":ArgType,
                "VarScopeName":f"main"
            }     

            OldEnv = self.EnvironmentList.pop()
            self.Environment = self.EnvironmentList[-1]
            self.Environment.declarefunc(Name.get("Value"), Tree)
            self.EnvironmentList.append(OldEnv)
            self.Environment = OldEnv
                   
            GotReturn = False
            self.Expected(TokenType.Sym, "{")
            while self.not_eof() or self.GetVT(self.At(), TokenType.Sym, "}") != True:
                if self.At().get("Type") == TokenType.EOF:
                    break
                if self.GetVT(self.At(), TokenType.Sym, "}") == True:
                    break


                Pos = self.Tokenscount

                Node = self.parse_stmt()
                if Node.get("Type") == Satement.RetStmt:
                    if RetType.get("Value") == "int":
                        if Node.get("Value").get("Type") not in [TokenType.Int, Expression.BinExpr]: # type: ignore
                            if Node.get("Value").get("Type")== Expression.VarCallExpr: # type: ignore
                                if Node.get("Value").get("VarType") not in ["int", "float"]: # type: ignore
                                    print(f"{Style.BRIGHT}{self.FileName}:{self.Line[Pos + 1]}:{self.Coloum[Pos + 1]}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} '{Name.get("Value")}' expects an return type of 'int'")
                                    print(f"{self.Line[Pos + 1]}|{self.SourceLines[self.Line[Pos + 1] - 1]}")
                                    print(f"{len(str(self.Line[Pos + 1])) * " "}|{Fore.RED}{(self.Coloum[Pos + 2] - 1) * " "}{(self.Coloumend[Pos + 2] - self.Coloum[Pos + 2]) * "~"}{Fore.RESET}")
                                    self.ErrorCount+=1
                            elif Node.get("Value").get("Type") == Expression.FuncCallExpr: # type: ignore
                                if Node.get("Value").get("ReturnType") not in ["int", "float"]: # type: ignore
                                
                                    print(f"{Style.BRIGHT}{self.FileName}:{self.Line[Pos + 1]}:{self.Coloum[Pos + 1]}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} '{Name.get("Value")}' expects an return type of 'int'")
                                    print(f"{self.Line[Pos + 1]}|{self.SourceLines[self.Line[Pos + 1] - 1]}")
                                    print(f"{len(str(self.Line[Pos + 1])) * " "}|{Fore.RED}{(self.Coloum[Pos + 2] - 1) * " "}{(self.Coloumend[Pos + 2] - self.Coloum[Pos + 2]) * "~"}{Fore.RESET}")
                                    self.ErrorCount+=1  
                            else:
                                print(f"{Style.BRIGHT}{self.FileName}:{self.Line[Pos + 1]}:{self.Coloum[Pos + 1]}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} '{Name.get("Value")}' expects an return type of 'int'")
                                print(f"{self.Line[Pos + 1]}|{self.SourceLines[self.Line[Pos + 1] - 1]}")
                                print(f"{len(str(self.Line[Pos + 1])) * " "}|{Fore.RED}{(self.Coloum[Pos + 2] - 1) * " "}{(self.Coloumend[-1] - self.Coloum[Pos + 2]) * "~"}{Fore.RESET}")
                                self.ErrorCount+=1   
                if Node.get("Type") == Satement.FuncDecStmt:
                    print(f"{Style.BRIGHT}{self.FileName}:{self.Line[Pos + 1]}:{self.Coloum[Pos + 1]}: {Style.RESET_ALL}{Fore.RED}SyntaxError:{Fore.RESET} A function can not contain another function")
                    print(f"{self.Line[Pos + 1]}|{self.SourceLines[self.Line[Pos + 1] - 1]}")
                    print(f"{len(str(self.Line[Pos + 1])) * " "}|{Fore.RED}{self.SourceLines[self.Line[Pos + 1] - 1].find("func") * " "}{(self.SourceLines[self.Line[Pos + 1] - 1].find(":") - self.SourceLines[self.Line[Pos + 1] - 1].find("func")) * "~"}{Fore.RESET}")
                    self.ErrorCount+=1    

                Body.append(Node)
            
            self.Expected(TokenType.Sym, "}")
        



            Tree = {
                "Type":Program.Main,
                "ReturnType":RetType.get("Value"),
                "Name":Name.get("Value"),
                "Args":Args,
                "Body":Body,
                "ArgTypes":ArgType,
                "VarScopeName":"main"
            }     

            self.EnvironmentList.pop()
            self.Environment = self.EnvironmentList[-1]
            self.Environment.Assingfunc(Name.get("Value"), Tree)
            return Tree
        
        #---Non Main Functions-----    
        self.Expected(TokenType.Op, ":")
        RetType = self.ExpectedType(TokenType.Data, ":")

        ScopeName = f"_{self.Environment.ScopeNum}"
        self.EnvironmentNum+=1
        self.Environment = Environment(self.Environment, self.EnvironmentNum)
        self.EnvironmentList.append(self.Environment)
        
        
        Args = self.parse_args()

        ArgType = {}
        for idex, i in enumerate(Args): # type: ignore
            AType = i.get("VarType") # type: ignore
            ArgType.update({idex:AType})

        Body = []
        Tree = {
            "Type":Satement.FuncDecStmt,
            "ReturnType":RetType.get("Value"),
            "Name":Name.get("Value"),
            "Args":Args,
            "Body":Body,
            "ArgTypes":ArgType,
            "VarScopeName":f"{Name.get("Value")}{ScopeName}"
        }     

        # To Add Recursivnes
        OldEnv = self.EnvironmentList.pop()
        self.Environment = self.EnvironmentList[-1]
        self.Environment.declarefunc(Name.get("Value"), Tree)
        self.EnvironmentList.append(OldEnv)
        self.Environment = OldEnv

        
        GotReturn = False
        self.Expected(TokenType.Sym, "{")
        while self.not_eof() or self.GetVT(self.At(), TokenType.Sym, "}") != True:
            if self.At().get("Type") == TokenType.EOF:
                break
            if self.GetVT(self.At(), TokenType.Sym, "}") == True:
                break

            Pos = self.Tokenscount

            Node = self.parse_stmt()
            if Node.get("Type") == Satement.RetStmt:
                if RetType.get("Value") == "int":
                    if Node.get("Value").get("Type") not in [TokenType.Int, Expression.BinExpr]: # type: ignore
                        if Node.get("Value").get("Type")== Expression.VarCallExpr: # type: ignore
                            if Node.get("Value").get("VarType") not in ["int", "float"]: # type: ignore
                                print(f"{Style.BRIGHT}{self.FileName}:{self.Line[Pos + 1]}:{self.Coloum[Pos + 1]}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} '{Name.get("Value")}' expects an return type of 'int'")
                                print(f"{self.Line[Pos + 1]}|{self.SourceLines[self.Line[Pos + 1] - 1]}")
                                print(f"{len(str(self.Line[Pos + 1])) * " "}|{Fore.RED}{(self.Coloum[Pos + 2] - 1) * " "}{(self.Coloumend[Pos + 2] - self.Coloum[Pos + 2]) * "~"}{Fore.RESET}")
                                self.ErrorCount+=1
                        elif Node.get("Value").get("Type") == Expression.FuncCallExpr: # type: ignore
                            if Node.get("Value").get("ReturnType") not in ["int", "float"]: # type: ignore
                                
                                print(f"{Style.BRIGHT}{self.FileName}:{self.Line[Pos + 1]}:{self.Coloum[Pos + 1]}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} '{Name.get("Value")}' expects an return type of 'int'")
                                print(f"{self.Line[Pos + 1]}|{self.SourceLines[self.Line[Pos + 1] - 1]}")
                                print(f"{len(str(self.Line[Pos + 1])) * " "}|{Fore.RED}{(self.Coloum[Pos + 2] - 1) * " "}{(self.Coloumend[Pos + 2] - self.Coloum[Pos + 2]) * "~"}{Fore.RESET}")
                                self.ErrorCount+=1  
                        else:
                            print(f"{Style.BRIGHT}{self.FileName}:{self.Line[Pos + 1]}:{self.Coloum[Pos + 1]}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} '{Name.get("Value")}' expects an return type of 'int'")
                            print(f"{self.Line[Pos + 1]}|{self.SourceLines[self.Line[Pos + 1] - 1]}")
                            print(f"{len(str(self.Line[Pos + 1])) * " "}|{Fore.RED}{(self.Coloum[Pos + 2] - 1) * " "}{(self.Coloumend[-1] - self.Coloum[Pos + 2]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1   
            if Node.get("Type") == Satement.FuncDecStmt:
                print(f"{Style.BRIGHT}{self.FileName}:{self.Line[Pos + 1]}:{self.Coloum[Pos + 1]}: {Style.RESET_ALL}{Fore.RED}SyntaxError:{Fore.RESET} A function can not contain another function")
                print(f"{self.Line[Pos + 1]}|{self.SourceLines[self.Line[Pos + 1] - 1]}")
                print(f"{len(str(self.Line[Pos + 1])) * " "}|{Fore.RED}{self.SourceLines[self.Line[Pos + 1] - 1].find("func") * " "}{(self.SourceLines[self.Line[Pos + 1] - 1].find(":") - self.SourceLines[self.Line[Pos + 1] - 1].find("func")) * "~"}{Fore.RESET}")
                self.ErrorCount+=1    
                
                GotReturn = True
            Body.append(Node)
        
        if GotReturn != True and RetType.get("Value") != "void":
            print(f"{Style.BRIGHT}{self.FileName}:{self.Line[-1]}:{self.Coloum[-1]}: {Style.RESET_ALL}{Fore.MAGENTA}Warning:{Fore.RESET} '{Name.get("Value")}' does not return a value this may cause errors try:")
            print(f"func {Name.get("Value")}: {RetType.get("Value")}({Fore.GREEN}/* Your Arguments*/{Fore.RESET})" + "{")
            print(f"{Fore.GREEN}\t/*\n\n\tYour Code\n\n\t*/{Fore.RESET}")
            if RetType.get("Value") == "int":
                print(f"\treturn 0; {Fore.GREEN}//To Return Nothing in some way{Fore.RESET}" + "\n}\n")
        self.Expected(TokenType.Sym, "}")




        Tree = {
            "Type":Satement.FuncDecStmt,
            "ReturnType":RetType.get("Value"),
            "Name":Name.get("Value"),
            "Args":Args,
            "Body":Body,
            "ArgTypes":ArgType,
            "VarScopeName":f"{Name.get("Value")}{ScopeName}"
        }     

        self.EnvironmentList.pop()
        self.Environment = self.EnvironmentList[-1]
        self.Environment.Assingfunc(Name.get("Value"), Tree)
        return Tree


    def parse_args(self):
        self.Expected(TokenType.Sym, "(")
        Args = []
        while self.not_eof() or self.GetVT(self.At(), TokenType.Sym, ")") != True:
            if self.At().get("Type") == TokenType.EOF:
                break
            if self.GetVT(self.At(), TokenType.Sym, ")") == True:
                break
            DataType = self.ExpectedType(TokenType.Data, "function")
            Name = self.ExpectedType(TokenType.Iden, "function")

            value = {}
            if DataType.get("Value") == "int":
                value = {
                    "Type": "Integer_Literal",
                    "Value": "0",
                    "Coloum": 0,
                    "Line": 0
                }

            Tree = {
                "Type":Satement.ArgDecStmt ,
                "VarType":DataType.get("Value"),
                "IsConstant":False,
                "Name":Name.get("Value"),
                "Value":value
            }
            self.Environment.declarevar(Name.get("Value"), Tree)
            Args.append(Tree)

            if self.GetVT(self.At(), TokenType.Sym, ")"):
                pass
            elif self.GetVT(self.At(), TokenType.Sym, ","):
                self.eat()
             
        self.Expected(TokenType.Sym, ")")
        return Args

    def parse_var_dec_stmt(self):
        IsConst = self.eat()
        if (IsConst.get("Value") == "const") == True:
            DataType = self.ExpectedType(TokenType.Data, "const")
            Identifier = self.ExpectedType(TokenType.Iden, DataType.get("Type"))
            
            self.Expected(TokenType.Op, "=")

            Line = self.Line[-1]
            Coloum = self.Coloum[-1]
            End = self.Coloumend[-1]

            Value = self.parse_expr()

            if IsConst.get("Value") == "int":           
                if Value.get("Type") not in [Expression.BinExpr, TokenType.Int]:
                    print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} 'int' datatype expects an 'int' value")
                    print(f"{Line}|{self.SourceLines[Line - 1]}")
                    print(f"{len(str(Line)) * " "}|{Fore.RED}{End * " "}{(self.Coloumend[-1] - End) * "~"}{Fore.RESET}")
                    self.ErrorCount+=1          

            Tree = {
                "Type":Satement.VarDecStmt,
                "VarType":DataType.get("Value"),
                "IsConstant":True,
                "Name":Identifier.get("Value"),
                "Value":Value
            }

            self.Expected(TokenType.Sym, ";")
            self.Environment.declarevar(Identifier.get("Value"), Tree)
            return Tree

        Identifier = self.ExpectedType(TokenType.Iden, IsConst.get("Type"))
        if self.GetVT(self.At(), TokenType.Sym, ";"):
            self.eat()
            if IsConst.get("Value") == "int":
                Tree  = {
                    "Type":Satement.VarDecStmt,
                    "VarType":IsConst.get("Value"),
                    "IsConstant":False,
                    "Name":Identifier.get("Value"),
                    "Value":{
                        "Type": "Integer_Literal",
                        "Value": "0",
                        "Coloum": 0,
                        "Line": 0
                    }
                }
                self.Environment.declarevar(Identifier.get("Value"), Tree)
                return Tree
        
        if self.GetVT(self.At(), TokenType.Sym, "["):
            self.eat()
            Size = self.eat()
            self.Expected(TokenType.Sym, "]")

            self.Expected(TokenType.Op, "=")
            
            Body = []
            self.Expected(TokenType.Sym, "{")
            while self.not_eof() or self.GetVT(self.At(), TokenType.Sym, "}") != True:
                if self.At().get("Type") == TokenType.EOF:
                    break
                if self.GetVT(self.At(), TokenType.Sym, "}") == True:
                    break

                Node = self.parse_expr()
                if self.GetVT(self.At(), TokenType.Sym, ","):
                    self.eat()

                Body.append(Node)
            self.Expected(TokenType.Sym, "}")
            Tree = {
                "Type":Satement.ArrayDecStmt,
                "Typeof":IsConst.get("Value"),
                "Size":Size.get("Value"),
                "IsConstant":False,
                "Name":Identifier.get("Value"),
                "Elemets":Body
            }
            
            self.Environment.declarevar(Identifier.get("Value"), Tree)
            self.Expected(TokenType.Sym, ";")
            return Tree
            
            
        self.Expected(TokenType.Op, "=")
        
        Line = self.Line[-1]
        Coloum = self.Coloum[-1]
        End = self.Coloumend[-1]


        Value = self.parse_expr()
    
            
        if IsConst.get("Value") == "int":           
            if Value.get("Type") not in [Expression.BinExpr, TokenType.Int]:
                print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} 'int' datatype expects an 'int' value")
                print(f"{Line}|{self.SourceLines[Line - 1]}")
                print(f"{len(str(Line)) * " "}|{Fore.RED}{End * " "}{(self.Coloumend[-1] - End) * "~"}{Fore.RESET}")
                self.ErrorCount+=1  

        Tree  = {
            "Type":Satement.VarDecStmt,
            "VarType":IsConst.get("Value"),
            "IsConstant":False,
            "Name":Identifier.get("Value"),
            "Value":Value
        }

        self.Expected(TokenType.Sym, ";")
        self.Environment.declarevar(Identifier.get("Value"), Tree)
        return Tree 
        
    def parse_while_stmt(self):
        self.eat()

        self.Expected(TokenType.Sym, "(")
        Condition = self.parse_expr()
        self.Expected(TokenType.Sym, ")")

        self.EnvironmentNum+=1
        self.Environment = Environment(self.Environment, self.EnvironmentNum)
        self.EnvironmentList.append(self.Environment)

        Body = []
        self.Expected(TokenType.Sym, "{")
        while self.not_eof() or self.GetVT(self.At(), TokenType.Sym, "}") != True:
            if self.At().get("Type") == TokenType.EOF:
                break
            if self.GetVT(self.At(), TokenType.Sym, "}") == True:
                break

            Node = self.parse_stmt()
            Body.append(Node)
        self.Expected(TokenType.Sym, "}")

        self.EnvironmentList.pop()
        self.Environment = self.EnvironmentList[-1]

        Tree = {
            "Type":Satement.WhileStmt,
            "Condition":Condition,
            "Body":Body
        }

        return Tree
 
    def parse_if_stmt(self):
        self.eat()
        self.Expected(TokenType.Sym, "(")
        Condition = self.parse_expr()
        self.Expected(TokenType.Sym, ")")

        self.EnvironmentNum+=1
        self.Environment = Environment(self.Environment, self.EnvironmentNum)
        self.EnvironmentList.append(self.Environment)

        Consequent = []
        self.Expected(TokenType.Sym, "{")
        while self.not_eof() or self.GetVT(self.At(), TokenType.Sym, "}") != True:
            if self.At().get("Type") == TokenType.EOF:
                break
            if self.GetVT(self.At(), TokenType.Sym, "}") == True:
                break

            Node = self.parse_stmt()
            Consequent.append(Node)
        self.Expected(TokenType.Sym, "}")

        self.EnvironmentList.pop()
        self.Environment = self.EnvironmentList[-1]

        if self.GetVT(self.At(), TokenType.Key, "elif"):
            Alternate = self.parse_elif_stmt()

        elif self.GetVT(self.At(), TokenType.Key, "else"):
            Alternate = self.parse_else_stmt()
        else:
            Alternate = None

        Tree = {
            "Type":Satement.IfStmt,
            "Condition":Condition,
            "Consequent":Consequent,
            "Alternate":Alternate
        }

        return Tree

    def parse_elif_stmt(self):
        self.eat()
        self.Expected(TokenType.Sym, "(")
        Condition = self.parse_expr()
        self.Expected(TokenType.Sym, ")")

        self.EnvironmentNum+=1
        self.Environment = Environment(self.Environment, self.EnvironmentNum)
        self.EnvironmentList.append(self.Environment)

        Consequent = []
        self.Expected(TokenType.Sym, "{")
        while self.not_eof() or self.GetVT(self.At(), TokenType.Sym, "}") != True:
            if self.At().get("Type") == TokenType.EOF:
                break
            if self.GetVT(self.At(), TokenType.Sym, "}") == True:
                break

            Node = self.parse_stmt()
            Consequent.append(Node)
        self.Expected(TokenType.Sym, "}")

        self.EnvironmentList.pop()
        self.Environment = self.EnvironmentList[-1]

        if self.GetVT(self.At(), TokenType.Key, "elif"):
            Alternate = self.parse_elif_stmt()

        elif self.GetVT(self.At(), TokenType.Key, "else"):
            Alternate = self.parse_else_stmt()
        else:
            Alternate = None

        Tree = {
            "Type":Satement.ElifStmt,
            "Condition":Condition,
            "Consequent":Consequent,
            "Alternate":Alternate
        }

        return Tree

    def parse_else_stmt(self):
        self.eat()

        self.EnvironmentNum+=1
        self.Environment = Environment(self.Environment, self.EnvironmentNum)
        self.EnvironmentList.append(self.Environment)

        Consequent = []
        self.Expected(TokenType.Sym, "{")
        self.EnvironmentList.pop()
        self.Environment = self.EnvironmentList[-1]
        
        while self.not_eof() or self.GetVT(self.At(), TokenType.Sym, "}") != True:
            if self.At().get("Type") == TokenType.EOF:
                break
            if self.GetVT(self.At(), TokenType.Sym, "}") == True:
                break

            Node = self.parse_stmt()
            Consequent.append(Node)
        self.Expected(TokenType.Sym, "}")



        Tree = {
            "Type":Satement.ElseStmt,
            "Consequent":Consequent,
        }

        return Tree

    def parse_import_stmt(self):
        from json import dumps

        self.eat()
        FileName = self.ExpectedType(TokenType.Str, "import")


        try:
            with open(FileName.get("Value")[1:-1], "r") as File:
                SourceCode = File.read()
                SourceCode+='\n'
        except FileNotFoundError:
            try:
                with open(f"C:\\Users\\Devvy\\Desktop\\Compiler\\src\\inc\\{FileName.get("Value")[1:-1]}", "r") as File: 
                    SourceCode = File.read()
                    SourceCode+='\n'
            except:
                Line = self.Line[-1]
                Coloum = self.Coloum[-1]
                End = self.Coloumend[-1]

                print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}ImportError:{Fore.RESET} '{FileName.get("Value")[1:-1]}' no such file, directory or libary")
                print(f"{Line}|{self.SourceLines[Line - 1]}")
                print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum - 1) * " "}{(self.Coloumend[-1] - self.Coloum[-1]) * "~"}{Fore.RESET}")
                self.ErrorCount+=1  
                return {}
            
        if FileName.get("Value")[1:-1] not in self.ImportTable:
            LexClass = Lexer(FileName.get("Value")[1:-1], SourceCode)
            LexTokens = LexClass.Lexer()

            #fix this
            ParseClass = Parser(SourceCode.split('\n'), LexTokens, FileName.get("Value")[1:-1], self.Environment, self.ImportTable)
            Ast = ParseClass.Parser()

            self.EnvironmentNum = ParseClass.Environment.ScopeNum
            self.Environment = ParseClass.Environment
            self.EnvironmentList = ParseClass.EnvironmentList

            self.EvalImport = True
            return Ast

        return {
            "Import":FileName.get("Value")[1:-1]
        }

    def parse_println_stmt(self):
        self.eat()
        Arguments = self.parse_print_args()
        Tree = {
            "Type":Satement.PrintStmt,
            "Arguments":Arguments
        }

        self.Expected(TokenType.Sym, ";")
        return Tree

    def parse_print_args(self):
        Args = []

        while self.not_eof() or self.GetVT(self.At(), TokenType.Sym, ";") != True:
            if self.At().get("Type") == TokenType.EOF:
                break
            if self.GetVT(self.At(), TokenType.Sym, ";") == True:
                break
            
            self.Expected(TokenType.Op, ">>")
            Args.append(self.parse_expr())
        
        return Args

    def parse_return_stmt(self):
        self.eat()
        ReturnVal = self.parse_expr()
        if self.GetVT(ReturnVal, TokenType.Sym, ";"):
            Tree = {
                "Type":Satement.RetStmt,
                "Value":{
                    "Type": "Integer_Literal",
                    "Value": "0",
                    "Coloum": 0,
                    "Line": 0
                }
            }
            return Tree
        else:
            Tree = {
                "Type":Satement.RetStmt,
                "Value":ReturnVal
            }
            self.Expected(TokenType.Sym, ";")
            return Tree
        
    def parse_exit_stmt(self):
        self.eat()
        Line = self.Line[-1]
        Coloum = self.Coloum[-1]
        End = self.Coloumend[-1]

        ExitCode = self.parse_expr()
        Tree = {
            "Type":Satement.ExitStmt,
            "ExitCode":ExitCode
        }


        if ExitCode.get("Type") not in [TokenType.Int, Expression.BinExpr, Expression.IncExpr, Expression.DecExpr]:
            if ExitCode.get("Type") == Expression.VarCallExpr:
                if ExitCode.get("VarType") != "int":
                    print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Exit expects some form of 'int' type")
                    print(f"{Line}|{self.SourceLines[Line - 1]}")
                    print(f"{len(str(Line)) * " "}|{Fore.RED}{End * " "}{(self.Coloumend[-1] - self.Coloum[-1]) * "~"}{Fore.RESET}")
                    self.ErrorCount+=1
            elif ExitCode.get("Type") == Expression.FuncCallExpr:
                if ExitCode.get("ReturnType") != "int":
                    print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Exit expects some form of 'int' type")
                    print(f"{Line}|{self.SourceLines[Line - 1]}")
                    print(f"{len(str(Line)) * " "}|{Fore.RED}{End * " "}{(self.Coloumend[-1] - self.Coloum[-1]) * "~"}{Fore.RESET}")
                    self.ErrorCount+=1
            else:
                print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Exit expects some form of 'int' type")
                print(f"{Line}|{self.SourceLines[Line - 1]}")
                print(f"{len(str(Line)) * " "}|{Fore.RED}{End * " "}{(self.Coloumend[-1] - self.Coloum[-1]) * "~"}{Fore.RESET}")
                self.ErrorCount+=1
        if self.FoundFloat == True:
            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Exit expects some form of 'int' type")
            print(f"{Line}|{self.SourceLines[Line - 1]}")
            print(f"{len(str(Line)) * " "}|{Fore.RED}{End * " "}{(self.Coloumend[-1] - self.Coloum[-1]) * "~"}{Fore.RESET}")
            self.ErrorCount+=1            

        self.Expected(TokenType.Sym, ";")
        return Tree

    def parse_expr(self):
        return self.parse_comparison_expr()

    def parse_comparison_expr(self):
        Left = self.parse_Rel_comparison_expr()
        while(self.GetVT(self.At(), TokenType.Op, "==") or self.GetVT(self.At(), TokenType.Op, "!=")):
            Operator = self.eat()
            Right = self.parse_Rel_comparison_expr()

            Left = {
                "Type":Expression.CompExpr,
                "Left":Left,
                "Right":Right,
                "Operator":Operator
            }
        
        return Left
    
    def parse_Rel_comparison_expr(self):
        Left = self.parse_additive_expr()
        while(self.GetVT(self.At(), TokenType.Op, ">") or self.GetVT(self.At(), TokenType.Op, "<") or self.GetVT(self.At(), TokenType.Op, "<=") or self.GetVT(self.At(), TokenType.Op, ">=")):
            Operator = self.eat()
            Right = self.parse_additive_expr()

            Left = {
                "Type":Expression.CompExpr,
                "Left":Left,
                "Right":Right,
                "Operator":Operator
            }
        
        return Left

    def parse_additive_expr(self):

        Left = self.parse_multipicitive_expr()

        if self.GetVT(self.At(), TokenType.Op, "+") == True and Left.get("Type") in [TokenType.Str, Expression.CatExpr]:
            while(self.GetVT(self.At(), TokenType.Op, "+")):
                Operator = self.eat()
                Right = self.parse_multipicitive_expr()
                if Right.get("Type") not in [TokenType.Str, Expression.CatExpr] or Left.get("Type") not in [TokenType.Str, Expression.CatExpr]:
                    if Right.get("Type") == Expression.VarCallExpr:
                        if Right.get("VarType") not in ["int", "float"]:
                            Linelist = self.Line[-3:]
                            Coloum = self.Coloum[-3:]
                            End = self.Coloumend[-3:]
                            Line = min(Linelist)
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                            print(f"{Line}|{self.SourceLines[Line - 1]}")
                            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1
                    elif Left.get("Type") == Expression.VarCallExpr:
                        if Left.get("VarType") not in ["int", "float"]:
                            Linelist = self.Line[-3:]
                            Coloum = self.Coloum[-3:]
                            End = self.Coloumend[-3:]
                            Line = min(Linelist)
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                            print(f"{Line}|{self.SourceLines[Line - 1]}")
                            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1
 

                    else:
                        Linelist = self.Line[-3:]
                        Coloum = self.Coloum[-3:]
                        End = self.Coloumend[-3:]
                        Line = min(Linelist)
                        print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                        print(f"{Line}|{self.SourceLines[Line - 1]}")
                        print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                        self.ErrorCount+=1

                Left = {
                    "Type":Expression.CatExpr,
                    "Left":Left,
                    "Right":Right
                }
        
            return Left

        while(self.GetVT(self.At(), TokenType.Op, "+") or self.GetVT(self.At(), TokenType.Op, "-")):
            Operator = self.eat()
            Right = self.parse_multipicitive_expr()

            #--Operand ismatch error---
            if Right.get("Type") not in [TokenType.Int, Expression.BinExpr, TokenType.Float] or Left.get("Type") not in [TokenType.Int, Expression.BinExpr, TokenType.Float]:
                    if Right.get("Type") == Expression.VarCallExpr:
                        if Right.get("VarType") not in ["int", "float"]:
                            Linelist = self.Line[-3:]
                            Coloum = self.Coloum[-3:]
                            End = self.Coloumend[-3:]
                            Line = min(Linelist)
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                            print(f"{Line}|{self.SourceLines[Line - 1]}")
                            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1
                    elif Right.get("Type") == Expression.FuncCallExpr:
                        if Right.get("ReturnType") not in ["int", "float"]:
                            Linelist = self.Line[-3:]
                            Coloum = self.Coloum[-3:]
                            End = self.Coloumend[-3:]
                            Line = min(Linelist)
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                            print(f"{Line}|{self.SourceLines[Line - 1]}")
                            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1
                    elif Right.get("Type") == Expression.ArrayAccExpr:
                        if Right.get("VarType") not in ["int", "float"]:
                            Linelist = self.Line[-3:]
                            Coloum = self.Coloum[-3:]
                            End = self.Coloumend[-3:]
                            Line = min(Linelist)
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                            print(f"{Line}|{self.SourceLines[Line - 1]}")
                            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1    

                    elif Left.get("Type") == Expression.VarCallExpr:
                        if Left.get("VarType") not in ["int", "float"]:
                            Linelist = self.Line[-3:]
                            Coloum = self.Coloum[-3:]
                            End = self.Coloumend[-3:]
                            Line = min(Linelist)
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                            print(f"{Line}|{self.SourceLines[Line - 1]}")
                            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1
                    elif Left.get("Type") == Expression.FuncCallExpr:
                        if Left.get("ReturnType") not in ["int", "float"]:
                            Linelist = self.Line[-3:]
                            Coloum = self.Coloum[-3:]
                            End = self.Coloumend[-3:]
                            Line = min(Linelist)
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                            print(f"{Line}|{self.SourceLines[Line - 1]}")
                            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1
                    elif Left.get("Type") == Expression.ArrayAccExpr:
                        if Left.get("VarType") not in ["int", "float"]:
                            Linelist = self.Line[-3:]
                            Coloum = self.Coloum[-3:]
                            End = self.Coloumend[-3:]
                            Line = min(Linelist)
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                            print(f"{Line}|{self.SourceLines[Line - 1]}")
                            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1                            
                    else:   
                        Linelist = self.Line[-3:]
                        Coloum = self.Coloum[-3:]
                        End = self.Coloumend[-3:]
                        Line = min(Linelist)
                        print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                        print(f"{Line}|{self.SourceLines[Line - 1]}")
                        print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                        self.ErrorCount+=1

            Left = {
                "Type":Expression.BinExpr,
                "Left":Left,
                "Right":Right,
                "Operator":Operator
            }
        return Left

    def parse_multipicitive_expr(self):
        Current_Type = Expression.BinExpr 

        Left = self.parse_primary_expr()
        while(self.GetVT(self.At(), TokenType.Op, "*") or self.GetVT(self.At(), TokenType.Op, "/") or self.GetVT(self.At(), TokenType.Op, "%")):
            Operator = self.eat()
            Right = self.parse_primary_expr()

            #--Throw Operand Errors
            if Right.get("Type") not in [TokenType.Int, Expression.BinExpr, TokenType.Float] or Left.get("Type") not in [TokenType.Int, Expression.BinExpr, TokenType.Float]:
                    if Right.get("Type") == Expression.VarCallExpr:
                        if Right.get("VarType") not in ["int", "float"]:
                            Linelist = self.Line[-3:]
                            Coloum = self.Coloum[-3:]
                            End = self.Coloumend[-3:]
                            Line = min(Linelist)
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                            print(f"{Line}|{self.SourceLines[Line - 1]}")
                            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1
                    elif Right.get("Type") == Expression.FuncCallExpr:
                        if Right.get("ReturnType") not in ["int", "float"]:
                            Linelist = self.Line[-3:]
                            Coloum = self.Coloum[-3:]
                            End = self.Coloumend[-3:]
                            Line = min(Linelist)
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                            print(f"{Line}|{self.SourceLines[Line - 1]}")
                            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1

                    elif Left.get("Type") == Expression.VarCallExpr:
                        if Left.get("VarType") not in ["int", "float"]:
                            Linelist = self.Line[-3:]
                            Coloum = self.Coloum[-3:]
                            End = self.Coloumend[-3:]
                            Line = min(Linelist)
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                            print(f"{Line}|{self.SourceLines[Line - 1]}")
                            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1
                    elif Left.get("Type") == Expression.FuncCallExpr:
                        if Left.get("ReturnType") not in ["int", "float"]:
                            Linelist = self.Line[-3:]
                            Coloum = self.Coloum[-3:]
                            End = self.Coloumend[-3:]
                            Line = min(Linelist)
                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                            print(f"{Line}|{self.SourceLines[Line - 1]}")
                            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                            self.ErrorCount+=1

                    else:
                        Linelist = self.Line[-3:]
                        Coloum = self.Coloum[-3:]
                        End = self.Coloumend[-3:]
                        Line = min(Linelist)
                        print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Operator.get("Coloum")}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Operand mismatch for '{Operator.get("Value")}' between '{self.Transalte(Left.get("Type"))}' and '{self.Transalte(Right.get("Type"))}'")
                        print(f"{Line}|{self.SourceLines[Line - 1]}")
                        print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum[0] - 1) * " "}{(Coloum[1] - Coloum[0]) * "~"}{(End[1] - Coloum[1]) * "^"}{(End[2] - End[1]) * "~"}{Fore.RESET}")
                        self.ErrorCount+=1

            Left = {
                "Type":Current_Type,
                "Left":Left,
                "Right":Right,
                "Operator":Operator
            }
        
        return Left

    def parse_func_call_expr(self):
        Name = self.eat()
        
        Value = self.Environment.Lookupfunc(Name.get("Value"))
        Args = []
        self.Expected(TokenType.Sym, "(")
        Line = self.At().get("Line")
        Coloum = self.At().get("Coloum")

        while self.not_eof() or self.GetVT(self.At(), TokenType.Sym, ")") != True:
            if self.At().get("Type") == TokenType.EOF:
                break
            if self.GetVT(self.At(), TokenType.Sym, ")") == True:
                break

            Args.append(self.parse_expr())

            if self.GetVT(self.At(), TokenType.Sym, ")"):
                pass
            elif self.GetVT(self.At(), TokenType.Sym, ","):
                self.eat()
        self.Expected(TokenType.Sym, ")")

        if len(Args) != len(Value.get("Args")):  # type: ignore
            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} '{Name.get("Value")}()' is missing {len(Value.get("Args")) - len(Args)} Arguments") # type: ignore
            print(f"{Line}|{self.SourceLines[Line - 1]}")
            self.ErrorCount+=1  

        ArgType = Value.get("ArgTypes") # type: ignore
        for index, i in enumerate(Args):
            if ArgType.get(index) == "int": # type: ignore
                if Args[index].get("Type") not in [TokenType.Int, Expression.BinExpr]: # type: ignore
                    if Args[index].get("Type") == Expression.VarCallExpr:
                        if Args[index].get("VarType") != "int":
                            Line = self.Line[-1]
                            Coloum = self.Coloum[-1]
                            End = self.Coloumend[-1]

                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Argument {index + 1}  in '{Name.get("Value")}()' recived incorrect type expected '{ArgType.get(index)}'") # type: ignore
                            print(f"{Line}|{self.SourceLines[Line - 1]}\n")
                            self.ErrorCount+=1 
                    elif Args[index].get("Type") == Expression.FuncCallExpr:
                        if Args[index].get("ReturnType") != "int":
                            Line = self.Line[-1]
                            Coloum = self.Coloum[-1]
                            End = self.Coloumend[-1]

                            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Argument {index + 1} in '{Name.get("Value")}()' recived incorrect type expected '{ArgType.get(index)}'") # type: ignore
                            print(f"{Line}|{self.SourceLines[Line - 1]}\n")
                            self.ErrorCount+=1 
                    else:
                        Line = self.Line[-1]
                        Coloum = self.Coloum[-1]
                        End = self.Coloumend[-1]

                        print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} Argument {index + 1}  in '{Name.get("Value")}()' recived incorrect type expected '{ArgType.get(index)}'") # type: ignore
                        print(f"{Line}|{self.SourceLines[Line - 1]}\n")
                        self.ErrorCount+=1 

        ArgType = Value.get("ArgTypes") # type: ignore
        
        Tree = {
            "Type":Expression.FuncCallExpr,
            "ReturnType":Value.get("ReturnType"), # type: ignore
            "Name":Value.get("Name"), # type: ignore
            "Args":Args,
            "ArgTypes":ArgType,
            "LookUpName":Value.get("VarScopeName") # type: ignore
        }

        return Tree
    
    def parse_var_call_expr(self):
        Name = self.At()
        if self.Environment.Resolvefunc(Name.get("Value")) != {}:
            return self.parse_func_call_expr()
        elif self.Environment.Resolve(Name.get("Value")) == {}:

            ret = self.eat()
            
            Line = self.Line[-1]
            Coloum = self.Coloum[-1]
            End = self.Coloumend[-1]

            print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}NameError:{Fore.RESET} '{Name.get("Value")}' Does not exist in this scope")
            print(f"{Line}|{self.SourceLines[Line - 1]}")
            print(f"{len(str(Line)) * " "}|{Fore.RED}{(Coloum - 1) * " "}{(self.Coloumend[-1] - self.Coloum[-1]) * "~"}{Fore.RESET}")
            self.ErrorCount+=1  
            return ret
        Name = self.eat()
        Value = self.Environment.LookupVar(Name.get("Value"))
        Call = {
            "Type":Expression.VarCallExpr,
            "VarType":Value.get("VarType"), # type: ignore
            "Name":Value.get("Name"), # type: ignore
            "LookUpName":Value.get("VarScopeName") # type: ignore
        }
        if Value.get("VarType") == "float": # type: ignore
            self.FoundFloat = True
        
        if self.At().get("Type") == TokenType.Op and self.At().get("Value") == "++":
            #Check If Its An Integer Or A fLoat Else Throw Errors
            Tree = {
                "Type":Expression.IncExpr,
                "Value":Call
            }
            self.eat()
            return Tree

        if self.At().get("Type") == TokenType.Op and self.At().get("Value") == "--":
            #Check If Its An Integer Or A fLoat Else Throw Errors
            Tree = {
                "Type":Expression.DecExpr,
                "Value":Call
            }
            self.eat()
            return Tree
        
        if self.GetVT(self.At(), TokenType.Sym, "["):
            self.eat()
            Pos = self.parse_expr()
            self.Expected(TokenType.Sym, "]")

            if self.GetVT(self.At(), TokenType.Op, "="):
                self.eat()
                Replaces = self.parse_expr()
                Tree  = {
                    "Type":Expression.ArrayRedifExpr,
                    "Position":Pos,
                    "ReplaceWith":Replaces,
                    "VarType":Value.get("Typeof"), # type: ignore
                    "Name":Value.get("Name"), # type: ignore
                    "LookUpName":Value.get("VarScopeName") # type: ignore
                }

                return Tree

            Tree = {
                "Type":Expression.ArrayAccExpr,
                "Position":Pos,
                "VarType":Value.get("Typeof"), # type: ignore
                "Name":Value.get("Name"), # type: ignore
                "LookUpName":Value.get("VarScopeName") # type: ignore
            }
  
            return Tree
        
        if self.GetVT(self.At(), TokenType.Op, "="):
            self.eat()

            Line = self.Line[-1]
            Coloum = self.Coloum[-1]
            End = self.Coloumend[-1]

            Value = self.parse_expr()

            self.Environment.AssingVar(self.At().get("Value"), Value)
            
            if self.Environment.LookupVar(Name.get("Value")).get("VarType") == "int":  # type: ignore  
                if Value.get("Type") not in [Expression.BinExpr, TokenType.Int]:
                    if Value.get("Type") == Expression.VarAssExpr:
                        pass
                    else:
                        print(f"{Style.BRIGHT}{self.FileName}:{Line}:{Coloum}: {Style.RESET_ALL}{Fore.RED}TypeError:{Fore.RESET} 'int' datatype expects redefinition value to be an 'int' type")
                        print(f"{Line}|{self.SourceLines[Line - 1]}")
                        print(f"{len(str(Line)) * " "}|{Fore.RED}{End * " "}{(self.Coloumend[-1] - End) * "~"}{Fore.RESET}")
                        self.ErrorCount+=1  

            Tree = {
                "Type":Expression.VarAssExpr,
                "Value":Value,
                "Name": Name.get("Value"),
                "VarType":self.Environment.LookupVar(Name.get("Value")).get("VarType"), # type: ignore
                "LookUpName":self.Environment.LookupVar(Name.get("Value")).get("VarScopeName") # type: ignore
            }
            
            return Tree
        return Call
    def parse_string_token(self):
        Token = self.eat()
        String = Token.get("Value")[1:-1]

        StringParts = []
        Pos = 0
        TempStr = '"'

        while(Pos < len(String)):
            if String[Pos] == "\\":
                StringParts.append(TempStr + '"')
                if String[Pos + 1] in ["n", "t"]:
                    StringParts.append(StringOptions(f"\\{String[Pos + 1]}").Hexi)
                    TempStr = '"'
                Pos+=1

            else:
                TempStr+=String[Pos]

            Pos+=1

        if TempStr != '"':
            StringParts.append(TempStr + '"')

        Token.update({"Parts":StringParts})
        return Token
    def parse_bool_token(self):
        Token = self.eat()
        Token["Type"] = TokenType.Int
        if Token.get("Value") == "true":
            Token["Value"] = "1"
        else:
            Token["Value"] = "0"
            
        return Token
            
    def parse_primary_expr(self):
        if self.GetVT(self.At(), TokenType.Sym, "("):
            Token = self.eat()
            Expr = self.parse_expr()
            self.Expected(TokenType.Sym, ")")
            return Expr
        elif self.At().get("Type") == TokenType.Float:
            self.FoundFloat = True
            return self.eat()
        elif self.At().get("Type") == TokenType.Iden:
            return self.parse_var_call_expr()
        elif self.At().get("Type") == TokenType.Str:
            return self.parse_string_token()
        elif self.At().get("Type") == TokenType.Bool:
            return self.parse_bool_token()
        else:
            return self.eat()
