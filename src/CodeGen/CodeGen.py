from src.Lexer.TokenTypes import TokenType
from src.Parser.AstTypes import Expression, Satement, Program

class CodeGen:
    def __init__(self, ExeName, ObjectName, AssemblyName, Path, Ast, Option):
        self.Ast = Ast
        self.Asm = AssemblyName
        self.Option = Option 
        self.Current_Lable = ""
        self.Path = Path
        self.Exe = ExeName
        self.Obj = ObjectName
        self.InMain = False

        #--Assembly Parts(Not All Lables)---
        self.Header = f";--Zedc verison 0.0.7--\n;--File '{self.Ast['File']}'--\n;--Headers--\nbits 64\ndefault rel"
        self.Data = "\n;----Know Variables--\nsection .data"
        self.Bss = "\n;---Unkown Vars---\nsection .bss"
        self.Text = "\n;--Code/Text Section--\nsection .text\n\tglobal main"
        self.Externs = "\n;--Imports/Extern--\nextern ExitProcess"
        self.Main = "\n;--Entry Point--"

        self.LinkTable = self.Ast.get("LinkTable")
        self.Defualt = ""

        self.AllocatePos = [2]
        self.SymbolTable = {

        }

        self.ExternTable = {
            "std_print":False,
            "std_print_int":False,
            "std_list_int":False,
        }

        self.HeaderIndent = 1
        self.DataIndent = 1
        self.TextIndent = 1
        self.ExternsIndent = 1
        self.MainIndent = 1
        self.CurrentLableIndent = 1
        self.BssLable = 1

        self.BasePointer = 0
        self.AloocatedSpace = 0

        self.BpList = [0]
        self.AllList = [0]
        self.FunctionSpace = 0

        self.MainLableCounter = 0

        self.CLable = ""
        self.ReachMain = False

        self.Args = 0

        self.StringNum = 0
        self.StrVar = 0

        self.CurrentRet = "void"

        self.IfCount = 0
        self.ElseCount = 0
        self.ElifCount = 0
        self.WhileCount = 0
        self.ContinueCount = 0
        self.JumpCont = False

        self.ArrayConut = 0

        self.JmpInst = "je"
        self.Lables = []
        self.ContinueList = []

        self.CreatedNumVar = False

        self.InFuc = "main"

    def OutMain(self, Info):
        self.Main+=f"\n{self.MainIndent * "\t"}{Info}"

    def OutData(self, Info):
        self.Data+=f"\n{self.DataIndent * "\t"}{Info}"

    def OutBss(self, Info):
        self.Bss+=f"\n{self.BssLable * "\t"}{Info}"

    def Alloc(self):
        Start = self.AllocatePos.pop() - 1
        End = len(self.Main.splitlines()) - 1
        SplitMain = self.Main.splitlines()

        def Round36(Number):
            x = (Number % 16) + Number
            if x == self.AloocatedSpace:
                return x + 16
            return x
        SplitMain[Start] = f"{SplitMain[Start]}\n\tpush rbp\n\tmov rbp, rsp\n\tsub rsp, {Round36(self.AloocatedSpace)}\n"
        SplitMain[End] =  f"{SplitMain[End]}\n\tmov rsp, rbp\n\tpop rbp\n"

        self.Main = '\n'.join(SplitMain)
        self.BasePointer-=self.AloocatedSpace
        self.AloocatedSpace = 0
    
    def CodeGen(self):
        self.Evaluate(self.Ast)
        self.MakeFile()

    def EvaluateProgram(self, Program):
        if Program.get('Name') == "main":
            self.InMain = True
            self.SymbolTable.update({Program.get("VarScopeName"):f"{Program.get("VarScopeName")}"})
            self.CLable = "main"
            self.Main+="\nmain:"
            self.AllocatePos.append(len(self.Main.splitlines()))
            self.ReachMain = True
            for statement in Program['Body']:
                self.Evaluate(statement)
            
            def Round36(Number):
                x = (Number % 16) + Number
                if x == self.AloocatedSpace:
                    return x + 16
                return x
        
            self.OutMain(f"add rsp, {Round36(self.AloocatedSpace)}")
            self.Alloc()
            self.OutMain(";Main Exit Program")
            self.OutMain("mov rcx, 0")
            self.OutMain("call ExitProcess")

        elif Program.get('Name') == "StartProgram":
            for statement in Program['Body']:
                self.Evaluate(statement)
            self.Main+="\n\n\n;Zed Compiler Project 'Zedc' offical Zed Compiler"
            self.Main+="\n;Credits: python, gcc, nasm"
    def MakeFile(self):
        if self.Option == "-s":
            with open(f"{self.Path}\\{self.Asm}", "w") as File:
                File.write(f"{self.Header}{self.Data}{self.Bss}{self.Text}{self.Externs}{self.Current_Lable}{self.Main}")
        if self.Option == "-e":
            import os
            import subprocess
            with open(f"{self.Path}\\{self.Asm}", "w") as File:
                File.write(f"{self.Header}{self.Data}{self.Bss}{self.Text}{self.Externs}{self.Current_Lable}{self.Main}") 

            import subprocess
            results = subprocess.run(["nasm", "-f", "elf64",  f"{self.Path}\\{self.Asm}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if results.returncode != 0:
                print("An Error ocurred while assembling")
                print(results.stderr.decode())
                exit(1)
            
            os.remove(f"{self.Path}\\{self.Asm}")

            if len(self.LinkTable) != 0:
                results = subprocess.run(["gcc", "-o", f"{self.Path}\\{self.Exe}", f"{self.Path}\\{self.Obj}", f"{' '.join(self.LinkTable)}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                results = subprocess.run(["gcc", "-o", f"{self.Path}\\{self.Exe}", f"{self.Path}\\{self.Obj}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if results.returncode != 0:
                print("An Error ocurred while linking")
                print(results.stderr.decode())  
                exit(1)    
            
            os.remove(f"{self.Path}\\{self.Obj}")
            
    def EvaluateFuncDecStmt(self, Node):
        self.InMain = False
        self.InFuc = Node.get("VarScopeName")
        if Node.get("ReturnType") in ["int", "str", "void"]:
            self.CurrentRet = Node.get("ReturnType")
            self.SymbolTable.update({Node.get("VarScopeName"):f"{Node.get("VarScopeName")}"})
            self.FunctionSpace+=8
            self.MainLableCounter+=1

            self.BpList.append(self.BasePointer)
            self.AllList.append(self.AloocatedSpace)

            self.BasePointer = 0
            self.AloocatedSpace = 0

            for index, i in enumerate(Node.get("Args")):
                self.Args+=1
            
            if self.ReachMain == True:
                self.OutMain(";jump to new program")
                self.OutMain(f"jmp main_{self.MainLableCounter}")
            
            self.Main+=f"\n{Node.get("VarScopeName")}:"
            self.AllocatePos.append(len(self.Main.splitlines()))

            argc = 1
            for i in list(Node.get("ArgTypes").keys()):
                
                if Node.get("ArgTypes").get(i) == "int":
                    self.FunctionSpace+=8
                if Node.get("ArgTypes").get(i) == "str":
                    self.FunctionSpace+=16 

            for i in list(Node.get("ArgTypes").keys()):
                
                if Node.get("ArgTypes").get(i) == "int":
                    self.BasePointer+=8
                    self.AloocatedSpace+=8
                    self.OutMain(f";Get argument {argc}")
                    self.OutMain(f"mov rax, [rbp+{self.FunctionSpace}]")
                    self.OutMain(f";Store the Argument {Node.get("Args")[int(i)].get("Name")}")
                    self.OutMain(f"mov  [rbp-{self.BasePointer}], rax")
                    self.SymbolTable.update({Node.get("Args")[int(i)].get("VarScopeName"):f"[rbp-{self.BasePointer}]"})
                    self.FunctionSpace-=8
                    argc+=1
                if Node.get("ArgTypes").get(i) == "str":
                    self.BasePointer+=8
                    self.AloocatedSpace+=8
                    self.OutMain(f";Get argument {argc}")
                    self.OutMain(f"mov rax, [rbp+{self.FunctionSpace}]")
                    self.OutMain(f";Store the Argument {Node.get("Args")[int(i)].get("Name")}")
                    self.OutMain(f"mov  [rbp-{self.BasePointer}], rax")

                    self.BasePointer+=8
                    self.FunctionSpace-=8
                    self.AloocatedSpace+=8
                    self.OutMain(f";Get argument {argc}")
                    self.OutMain(f"mov rax, [rbp+{self.FunctionSpace}]")
                    self.OutMain(f";Store the Argument {Node.get("Args")[int(i)].get("Name")}")
                    self.OutMain(f"mov  [rbp-{self.BasePointer}], rax")

                    self.SymbolTable.update({Node.get("Args")[int(i)].get("VarScopeName"):{
                        "Type":"str",
                        "Pointer":f"rbp-{self.BasePointer - 8}",
                        "Size":f"[rbp-{self.BasePointer}]"
                    }})

                    self.FunctionSpace-=8
                    argc+=1
            for i in Node.get("Body"):
                self.Evaluate(i)

            
            def Round36(Number):
                x = (Number % 16) + Number
                if x == self.AloocatedSpace:
                    return x + 16
                return x
        
            self.OutMain(f"add rsp, {Round36(self.AloocatedSpace)}")
            
            self.Alloc()
            self.OutMain("mov rax, 0")
            self.OutMain("ret")

            self.BasePointer = self.BpList.pop()
            self.AloocatedSpace = self.AllList.pop()

            if self.ReachMain == True:
                self.Main+=f"\nmain_{self.MainLableCounter}:"
            self.FunctionSpace = 0      
            self.InFuc = ""

    def EvaluateFuncCallExpr(self, Node):
        Arguments = []
        self.FunctionSpace = 0
        for i in Node.get("Args"):
            self.Evaluate(i)
        for i in list(Node.get("ArgTypes").keys()):
            if Node.get("ArgTypes").get(i) == "int":
                self.FunctionSpace+=8
            if Node.get("ArgTypes").get(i) == "str":
                self.FunctionSpace+=16

        if len(Arguments) != 0:
            for i in reversed(Arguments):
                self.OutMain(f"mov rax, {i}")
                self.OutMain("push rax")

        self.OutMain(f";call function {Node.get("Name")}")
        self.OutMain(f"call {self.SymbolTable.get(Node.get("LookUpName"))}")
        self.OutMain(f";push return val")
        self.OutMain(f"add rsp, {self.FunctionSpace}")

        if Node.get("ReturnType") == "int":
            self.OutMain(f"push rax")
        if Node.get("ReturnType") == "str":
            self.OutMain("push rbx")
            self.OutMain("push rax")
        self.FunctionSpace = 0
    def EvaluateArrayDecStatement(self, Node):
        if "src/Link_libs/ZedStdLib.o" not in self.LinkTable:
            self.LinkTable.append("src/Link_libs/ZedStdLib.o")

        self.OutBss(";Create a List")
        if Node.get("Typeof") == "int":
            self.OutBss(f"{Node.get("VarScopeName")} resq {int(Node.get("Size")) * 8}")
            if self.ExternTable['std_list_int'] == False:
                self.Externs+="\nextern std_list_int"
                self.ExternTable['std_list_int'] = True

            for i in Node.get("Elemets"):
                self.Evaluate(i)
            self.OutMain(";Get Array Size")
            self.OutMain(f"mov r11, {len(Node.get("Elemets"))}")
            self.Main+=f"\nAppend_Loop_{self.ArrayConut}:"
            self.OutMain(";Append The Item")
            self.OutMain("dec r11")
            self.OutMain("pop rax")
            self.OutMain(f"mov rcx, r11")
            self.OutMain(f"mov rsi, {Node.get("VarScopeName")}")
            self.OutMain("call std_list_int")
            self.OutMain("mov rdx, 0")
            self.OutMain("cmp rdx, r11")
            self.OutMain(f"jnz Append_Loop_{self.ArrayConut}")
            self.Main+=f"\nContinue_{self.ContinueCount}:"
            self.OutMain(f"lea rbx, {Node.get("VarScopeName")}")

            self.AloocatedSpace+=8
            self.BasePointer+=8
            self.OutMain(f"mov [rbp-{self.BasePointer}], rbx")
            self.SymbolTable.update({Node.get("VarScopeName"):f"[rbp-{self.BasePointer}]"})
            self.ContinueCount+=1

        self.ArrayConut+=1
    def EvaluateVarDecStmt(self, Node):
        self.Evaluate(Node.get("Value"))

        if Node.get("VarScopeName")[Node.get("VarScopeName").find("_") + 1] == "0":
            self.OutData(f";Make Global Variable {Node.get("Name")}")
            if Node.get("VarType") == "int":
                self.OutData(f"{Node.get("VarScopeName")} dq 0")
                self.OutMain(f";Store Data in variable {Node.get("Name")}")
                self.OutMain("pop rax")
                self.OutMain(f"mov [{Node.get("VarScopeName")}], rax")
                self.SymbolTable.update({Node.get("VarScopeName"):f"[{Node.get("VarScopeName")}]"})
        else:
            if Node.get("VarType") == "int":
                self.AloocatedSpace+=8
                self.BasePointer+=8

                self.OutMain(f";saves the variable '{Node.get("Name")}'")
                self.OutMain("pop rax")
                self.OutMain(f"mov [rbp-{self.BasePointer}], rax")
                self.SymbolTable.update({Node.get("VarScopeName"):f"[rbp-{self.BasePointer}]"})
            if Node.get("VarType") == "str":
                self.AloocatedSpace+=8
                self.BasePointer+=8

                
                self.OutMain("pop rax")
                self.OutMain(f"mov [rbp-{self.BasePointer}], rax")

                self.AloocatedSpace+=8
                self.BasePointer+=8

                self.OutMain(f";Store Variable {Node.get("Name")}")
                self.OutMain("pop rbx")
                self.OutMain(f"mov [rbp-{self.BasePointer}], rbx")



                self.SymbolTable.update({Node.get("VarScopeName"):{
                    "Type":"str",
                    "Pointer":f"rbp-{self.BasePointer}",
                    "Size":f"[rbp-{self.BasePointer - 8}]"
                }})

    def EvaluateAlternet(self, Node):
        if Node.get("Type") == Satement.IfStmt:
            self.EvaluateCondition(Node.get("Condition"))
            if Node.get("Alternate") != None:
                self.OutMain(f"{self.JmpInst} If_Stmt_{self.IfCount}")
                self.Lables.append(f"If_Stmt_{self.IfCount}")
                self.EvaluateAlternet(Node.get("Alternate"))
                self.IfCount+=1
            if Node.get("Alternate") == None:
                self.OutMain(f"{self.JmpInst} If_Stmt_{self.IfCount}")
                self.OutMain(f"jmp Continue_{self.ContinueCount}")
                self.Lables.append(f"If_Stmt_{self.IfCount}")
                self.ContinueList.append(f"Continue_{self.ContinueCount}")
                self.ContinueCount+=1
                self.IfCount+=1
        if Node.get("Type") == Satement.ElifStmt:
            self.EvaluateCondition(Node.get("Condition"))
            if Node.get("Alternate") != None:
                self.OutMain(f"{self.JmpInst} Elif_Stmt_{self.ElifCount}")
                self.Lables.append(f"Elif_Stmt_{self.ElifCount}")
                self.ElifCount+=1
                self.EvaluateAlternet(Node.get("Alternate"))
            if Node.get("Alternate") == None:
                self.OutMain(f"{self.JmpInst} Elif_Stmt_{self.ElifCount}")
                self.OutMain(f"jmp Continue_{self.ContinueCount}")
                self.Lables.append(f"Elif_Stmt_{self.ElifCount}")
                self.ContinueList.append(f"Continue_{self.ContinueCount}")
                self.ElifCount+=1
                self.ContinueCount+=1
        if Node.get("Type") == Satement.ElseStmt:
            self.OutMain(f"jmp Else_Stmt_{self.ElseCount}")
            self.OutMain(f"jmp Continue_{self.ContinueCount}")
            self.Lables.append(f"Else_Stmt_{self.ElseCount}")
            self.ContinueList.append(f"Continue_{self.ContinueCount}")
            self.ElseCount+=1
            self.ContinueCount+=1
    
    def EvaluateWhileStatement(self, Node):
        Condition = Node.get("Condition")
        WhileCon = self.WhileCount
        Continue = self.ContinueCount

        self.WhileCount+=1
        self.ContinueCount+=1

        self.Evaluate(Condition)
        self.OutMain(f"{self.JmpInst} While_Loop_{WhileCon}")
        self.Lables.append(f"While_Loop_{WhileCon}")
        self.ContinueList.append(f"Continue_{Continue}")
        self.OutMain(f"jmp Continue_{Continue}")

        self.Main+=f"\n{self.Lables[0]}:"
        self.Lables = self.Lables[1:]

        for i in Node.get("Body"):
            self.Evaluate(i)

        self.Evaluate(Condition)
        self.OutMain(f"{self.JmpInst} While_Loop_{WhileCon}")
        self.OutMain(f"jmp {self.ContinueList[0]}")

        self.Main+=f"\n{self.ContinueList[0]}:"
        self.ContinueList = self.ContinueList[1:]
        

    def EvaluateIfStatement(self, Node):
        self.EvaluateAlternet(Node)    

        self.Main+=f"\n{self.Lables[0]}:"
        self.Lables = self.Lables[1:]

        for i in Node.get("Consequent"):
            self.Evaluate(i)

        self.OutMain(f"jmp {self.ContinueList[0]}")

        if Node.get("Alternate") != None:
            self.Evaluate(Node.get("Alternate"))    

        self.Main+=f"\n{self.ContinueList[0]}:"
        self.ContinueList = self.ContinueList[1:]

    def EvaluateElifStatement(self, Node):
        self.Main+=f"\n{self.Lables[0]}:"
        self.Lables = self.Lables[1:]

        for i in Node.get("Consequent"):
            self.Evaluate(i)

        self.OutMain(f"jmp {self.ContinueList[0]}")

        if Node.get("Alternate") != None:
            self.Evaluate(Node.get("Alternate"))   

    def EvaluateElseStatement(self, Node):    
            
        self.Main+=f"\n{self.Lables[0]}:"
        self.Lables = self.Lables[1:]

        for i in Node.get("Consequent"):
            self.Evaluate(i)

        self.OutMain(f"jmp {self.ContinueList[0]}")  

    def EvaluateExitStatement(self, Node):
        self.Evaluate(Node.get("ExitCode"))

        self.OutMain(";Exits The Program")
        self.OutMain("pop rcx")
        self.OutMain("call ExitProcess")
        self.OutMain("")
    
    def EvaluatePrintStatement(self, Node):
        if "src/Link_libs/ZedStdLib.o" not in self.LinkTable:
            self.LinkTable.append("src/Link_libs/ZedStdLib.o")

        if self.ExternTable.get("std_print") == False:
            self.Externs+="\nextern std_print"
            self.ExternTable['std_print'] = True

        for i in Node.get("Arguments"):
            Type = self.Evaluate(i)
            if Type[0] == TokenType.Int:
                if self.ExternTable.get("std_print_int") == False:
                    self.Externs+="\nextern std_print_int"
                    self.ExternTable['std_print_int'] = True

                if self.CreatedNumVar == False:
                    self.OutBss("NumBuffer resb 21")
                    self.CreatedNumVar = True
                
                self.OutMain("pop rax")
                self.OutMain("mov rsi, NumBuffer")
                self.OutMain("call std_print_int")

                self.OutMain("mov r10, rcx")
                self.OutMain("lea rbx, NumBuffer")
                self.OutMain("call std_print")
            elif Type[0] == Expression.VarCallExpr:
                if Type[1].get("VarType") == "int":
                    if self.ExternTable.get("std_print_int") == False:
                        self.Externs+="\nextern std_print_int"
                        self.ExternTable['std_print_int'] = True

                    if self.CreatedNumVar == False:
                        self.OutBss("NumBuffer resb 21")
                        self.CreatedNumVar = True      

                    self.OutMain("pop rax")
                    self.OutMain("mov rsi, NumBuffer")
                    self.OutMain("call std_print_int")

                    self.OutMain("mov r10, rcx")
                    self.OutMain("lea rbx, NumBuffer")
                    self.OutMain("call std_print")     
                else:
                    if self.ExternTable.get("std_print") == False:
                        self.Externs+="\nextern std_print"
                        self.ExternTable['std_print'] = True


                    self.OutMain("pop r10")
                    self.OutMain("pop rbx")
                    self.OutMain("call std_print")    
            elif Type[0] ==  Expression.ArrayAccExpr:
                if Type[1].get("VarType") == "int":
                    if self.ExternTable.get("std_print_int") == False:
                        self.Externs+="\nextern std_print_int"
                        self.ExternTable['std_print_int'] = True

                    if self.CreatedNumVar == False:
                        self.OutBss("NumBuffer resb 21")
                        self.CreatedNumVar = True      

                    self.OutMain("pop rax")
                    self.OutMain("mov rsi, NumBuffer")
                    self.OutMain("call std_print_int")

                    self.OutMain("mov r10, rcx")
                    self.OutMain("lea rbx, NumBuffer")
                    self.OutMain("call std_print")     
            else:
                if self.ExternTable.get("std_print") == False:
                    self.Externs+="\nextern std_print"
                    self.ExternTable['std_print'] = True
   

                self.OutMain("pop r10")
                self.OutMain("pop rbx")
                self.OutMain("call std_print")

    def EvaluateReturnStatement(self, Node):
        self.Evaluate(Node.get("Value"))

        def Round36(Number):
            x = (Number % 16) + Number
            if x == self.AloocatedSpace:
                return x + 16
            return x
        
        if self.InMain == True:
            self.OutMain(";Exits the main function")
            self.OutMain("pop rcx")
            self.OutMain("call ExitProcess")

        elif self.CurrentRet == "int":
            self.OutMain(";Returns from function")
            self.OutMain("pop rax")
        
            self.OutMain(f"add rsp, {Round36(self.AloocatedSpace)}")
            self.OutMain("mov rsp, rbp")
            self.OutMain("pop rbp")
            self.OutMain("ret")
        
        elif self.CurrentRet == "str":
            self.OutMain(";Returns from function")
            self.OutMain("pop rax")
            self.OutMain("pop rbx")

            self.OutMain(f"add rsp, {Round36(self.AloocatedSpace)}")
            self.OutMain("mov rsp, rbp")
            self.OutMain("pop rbp")
            self.OutMain("ret")
        
        elif self.CurrentRet == "void":
            self.OutMain(f"add rsp, {Round36(self.AloocatedSpace)}")
            self.OutMain("mov rsp, rbp")
            self.OutMain("pop rbp")
            self.OutMain("ret")

    def EvaluateInteger(self, Node):
        Value = Node.get("Value")

        self.OutMain(";Pushes A Number")
        self.OutMain(f"push {Value}")

    def EvaluateArrayAccsesExpr(self, Node):
        self.Evaluate(Node.get("Position"))
        if Node.get("VarType") == "int":
            self.OutMain(";load adress")
            self.OutMain(f"mov rsi, {self.SymbolTable.get(Node.get("LookUpName"))}")
            self.OutMain(";Get Index Postion")
            self.OutMain("pop rbx")
            self.OutMain("mov rax, [rsi + rbx*8]")
            self.OutMain("push rax")
        
    def EvaluateArrayRedefinitionExpr(self, Node):
        if "src/Link_libs/ZedStdLib.o" not in self.LinkTable:
            self.LinkTable.append("src/Link_libs/ZedStdLib.o")

        self.Evaluate(Node.get("Position"))
        self.Evaluate(Node.get("ReplaceWith"))

        if Node.get("VarType") == "int":
            self.OutMain(";load adress")
            self.OutMain(f"mov rsi, {self.SymbolTable.get(Node.get("LookUpName"))}")
            self.OutMain(";Get New Value")
            self.OutMain("pop rax")
            self.OutMain(";Get Index Postion")
            self.OutMain("pop rcx")
            self.OutMain("call std_list_int")

    def EvaluateCondition(self, Node):
        self.Evaluate(Node.get("Left"))
        self.Evaluate(Node.get("Right"))
        self.OutMain("pop rax")
        self.OutMain("pop rbx")
        self.OutMain("cmp rbx, rax")

        if Node.get("Operator").get("Value") == "==":
            self.JmpInst = "je"
        if Node.get("Operator").get("Value") == "<=":
            self.JmpInst = "jle"
        if Node.get("Operator").get("Value") == "!=":
            self.JmpInst = "jne"
        if Node.get("Operator").get("Value") == ">=":
            self.JmpInst = "jge"
        if Node.get("Operator").get("Value") == ">":
            self.JmpInst = "jg"
        if Node.get("Operator").get("Value") == "<":
            self.JmpInst = "jl"

    def EvaluateDecrementExpr(self, Node):
        self.Evaluate(Node.get("Value"))

        self.OutMain(";Decrement A Variable")
        self.OutMain("pop rax")
        self.OutMain("dec rax")

        self.OutMain(f"mov  {self.SymbolTable.get(Node.get("Value").get("LookUpName"))}, rax")

    def EvaluateIncrementExpr(self, Node):
        self.Evaluate(Node.get("Value"))
        
        self.OutMain(";Increment A Variable")
        self.OutMain("pop rax")
        self.OutMain("inc rax")

        self.OutMain(f"mov  {self.SymbolTable.get(Node.get("Value").get("LookUpName"))}, rax")

    def EvaluateVarCallExpr(self, Node):
        if Node.get("VarType") == "int":
            self.OutMain(f";call Variable '{Node.get("Name")}'")
            self.OutMain(f"mov rax, {self.SymbolTable.get(Node.get("LookUpName"))}")
            self.OutMain("push rax")
        if Node.get("VarType") == "str":
            self.OutMain(f";Load the Adress of '{Node.get("Name")}'")
            self.OutMain(f"mov rbx, [{self.SymbolTable.get(Node.get("LookUpName")).get("Pointer")}]") # type: ignore
            self.OutMain("push rbx")

            self.OutMain(f";get the Size of '{Node.get("Name")}'")
            self.OutMain(f"mov rax, {self.SymbolTable.get(Node.get("LookUpName")).get("Size")}") # type: ignore
            self.OutMain(f"push rax")




    def EvaluateVarAssExpr(self, Node):
        self.Evaluate(Node.get("Value"))

        self.OutMain(";Moves new value into the variable")
        self.OutMain("pop rax")
        
        self.OutMain(f"mov  {self.SymbolTable.get(Node.get("LookUpName"))}, rax")
        #The Code May Cause Errors In THe Feature All It Does is Allow Chaning so i can do eg. x = y = u = 9;
        self.OutMain(f"mov rax, {self.SymbolTable.get(Node.get("LookUpName"))}")
        self.OutMain("push rax")
        
    def EvaluateBinaryExpression(self, Node):
        self.Evaluate(Node.get("Left"))
        self.Evaluate(Node.get("Right"))

        Operator = Node.get("Operator").get("Value")

        if Operator == "+":
            self.OutMain("pop rbx")
            self.OutMain("pop rax")
            self.OutMain(";Adds The Numbers Together")
            self.OutMain("add rax, rbx")
            self.OutMain("push rax")
        elif Operator == "-":
            self.OutMain("pop rbx")
            self.OutMain("pop rax")
            self.OutMain(";Subtracts The Numbers Together")
            self.OutMain("sub rax, rbx")
            self.OutMain("push rax")
        elif Operator == "*":
            self.OutMain("pop rbx")
            self.OutMain("pop rax")
            self.OutMain(";Multiplies two number")
            self.OutMain("imul rax, rbx")
            self.OutMain("push rax")
        elif Operator == "/":
            self.OutMain("pop rbx")
            self.OutMain("pop rax")
            self.OutMain(";cqo Extends divison for negative numbers")
            self.OutMain("cqo")
            self.OutMain(";Divides two numbers")
            self.OutMain("idiv rbx")
            self.OutMain(";Pushes the result to the top of the stack")
            self.OutMain("push rax")

    def EvaluateString(self, Node):
        self.OutData(f";Creates a String Var")
        self.Data+=f"\n\tString_{self.StringNum}:\n"
        self.Data+=f"\tdb "

        for Index, String in enumerate(Node.get("Parts")):
            self.Data+=f"{String}"
            if Index != (len(Node.get("Parts")) - 1):
                self.Data+=","
        
        self.Data+=", 0"
        self.OutData(f"\t.len equ $ - String_{self.StringNum}")

        self.OutMain(f"lea rbx, [String_{self.StringNum}]")
        self.OutMain(f"push rbx")
        self.OutMain(f"push String_{self.StringNum}.len")

        self.StringNum+=1

    def Evaluate(self, Node):
        if Node.get("Type") == Expression.BinExpr:
            self.EvaluateBinaryExpression(Node)
            return Expression.BinExpr, Node
        elif Node.get("Type") == Program.Prg:
            self.EvaluateProgram(Node)
            return Program.Prg, Node
        elif Node.get("Type") == Program.Main:
            self.EvaluateProgram(Node)
            return Program.Main, Node
        elif Node.get("Type") == TokenType.Int:
            self.EvaluateInteger(Node)
            return TokenType.Int, Node
        elif Node.get("Type") == TokenType.Str:
            self.EvaluateString(Node)
            return TokenType.Str, Node
        elif Node.get("Type") == Satement.FuncDecStmt:
            self.EvaluateFuncDecStmt(Node)
            return Satement.FuncDecStmt, Node
        elif Node.get("Type") == Satement.ExitStmt:
            self.EvaluateExitStatement(Node)
            return Satement.ExitStmt, Node
        elif Node.get("Type") == Satement.PrintStmt:
            self.EvaluatePrintStatement(Node)
            return Satement.PrintStmt     , Node
        elif Node.get("Type") == Satement.VarDecStmt:
            self.EvaluateVarDecStmt(Node)
            return Satement.VarDecStmt, Node
        elif Node.get("Type") == Expression.VarCallExpr:
            self.EvaluateVarCallExpr(Node)
            return Expression.VarCallExpr, Node
        elif Node.get("Type") == Expression.DecExpr:
            self.EvaluateDecrementExpr(Node)
            return Expression.DecExpr, Node
        elif Node.get("Type") == Expression.IncExpr:
            self.EvaluateIncrementExpr(Node)
            return Expression.DecExpr, Node
        elif Node.get("Type") == Expression.VarAssExpr:
            self.EvaluateVarAssExpr(Node)    
            return Expression.VarAssExpr, Node
        elif Node.get("Type") == Expression.FuncCallExpr:
            self.EvaluateFuncCallExpr(Node)
            return Expression.FuncCallExpr, Node
        elif Node.get("Type") == Satement.RetStmt:
            self.EvaluateReturnStatement(Node)
            return Satement.RetStmt, Node
        elif Node.get("Type") == Satement.IfStmt:
            self.EvaluateIfStatement(Node)
            return Satement.IfStmt, Node
        elif Node.get("Type") == Satement.ElseStmt:
            self.EvaluateElseStatement(Node)
            return Satement.ElseStmt, Node
        elif Node.get("Type") == Satement.ElifStmt:
            self.EvaluateElifStatement(Node)
            return Satement.ElifStmt, Node
        elif Node.get("Type") == Expression.CompExpr:
            self.EvaluateCondition(Node)
            return Expression.CompExpr, Node
        elif Node.get("Type") == Satement.WhileStmt:
            self.EvaluateWhileStatement(Node)
            return Satement.WhileStmt, Node
        elif Node.get("Type") == Satement.ArrayDecStmt:
            self.EvaluateArrayDecStatement(Node)
            return Satement.ArrayDecStmt, Node
        elif Node.get("Type") == Expression.ArrayAccExpr:
            self.EvaluateArrayAccsesExpr(Node)
            return Expression.ArrayAccExpr, Node
        elif Node.get("Type") == Expression.ArrayRedifExpr:
            self.EvaluateArrayRedefinitionExpr(Node)
            return Expression.ArrayRedifExpr, Node
        else:
            return Node