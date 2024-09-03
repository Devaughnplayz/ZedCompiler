class Program:
    Prg = "Program"
    Main = "Main_Start_Program"

class Satement:
    ExternStmt = "ExternStatement"
    ExitStmt = "ExitStatement"
    VarDecStmt = "VariableDeclartionStatement"
    FuncDecStmt = "FunctionDeclarationStatement"
    ArgDecStmt = "ArgumentDeclarationStatement"
    RetStmt = "ReturnStatement"
    PrintStmt = "PrintLineStatement"
    IfStmt = "IfStatement"
    ElifStmt = "ElifStatement"
    ElseStmt = "ElseStatement"
    WhileStmt = "WhileStatement"
    ArrayDecStmt = "ArrayDeclarationStatement"

class Expression(Satement):
    BinExpr = "BinaryExprssion"
    CatExpr = "ConCatExprssion"
    FloatBinExpr = "FloatBinaryExpression"
    VarCallExpr = "VariableCallExpression"
    IncExpr = "IncrementExpression"
    DecExpr = "DecrementExpression"
    VarAssExpr = "VariableAssingmentExpression"
    FuncCallExpr = "FunctionCallExpression"
    CompExpr =  "ComparisonExpression"
    Null = "Null"
    ArrayAccExpr = "ArrayAccsesExpression"
    ArrayRedifExpr = "ArrayRedefinitionExpression"
    
class StringOptions:
    def __init__(self, SplitType):
        self.SplitType = SplitType
        self.Hexi = ""

        if self.SplitType == "\\n":
            self.Hexi = "0Dh, 0Ah"
        if self.SplitType == "\\t":
            self.Hexi = "09h"
