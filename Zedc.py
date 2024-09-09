#--Imports---
from time import time

StartTime = time()

import colorama

colorama.init(autoreset=True)

from colorama import Fore

from sys import argv
argc = len(argv)

from json import dumps

import os
#--Compiler Infisturcutre--
from src.Lexer.Lexer import Lexer
from src.Parser.Parser import Parser
from src.CodeGen.CodeGen import CodeGen
from src.Environment.Enivironment import Environment

def main() -> None:
    if argc == 1:
        print(f"{Fore.RED}Fatal Error: {Fore.RESET}no input files compilation terminated")
        exit(1)
    if argc == 2 and argv[1] in ["-v", "--version"]:
        print("Zedc, offical compiler for Zed version 0.1.2")
        exit(0)
    if argc == 2 and argv[1] in ["-h", "--help"]:
        with open("Help.txt", "r") as File: 
            print(File.read())
            exit(0)

    #--Compile--
    try:
        with open(argv[1], "r") as File:
            SourceCode = File.read()
            SourceCode+='\n'
    except:
        print(f"{Fore.RED}Fatal Error: {Fore.RESET}'{argv[1]}' no such file or directory")
        exit(1)
    
    #--Lexer---
    LexerClass = Lexer(argv[1], SourceCode)
    LexedTokens = LexerClass.Lexer()
    
    
    #--Environment--
    GloablEnvironment = Environment()
    #--Parser--
    ParserClass = Parser(SourceCode.split('\n'), LexedTokens, argv[1], GloablEnvironment)
    Ast = ParserClass.Parser()
    


    #--CodeGeneration--
    if argc == 2:
        AssemblyName = "a.asm"
        ObjName = "a.o"
        Exe = "a.exe"
        Method = "-e"
    elif argc == 3:
        AssemblyName = "a.asm"
        ObjName = "a.o"
        Exe = "a.exe"
        Method = argv[2]    
    elif argc >= 4:
        AssemblyName = f"{argv[3]}.asm"
        ObjName = f"{argv[3]}.o"
        Exe = f"{argv[3]}.exe"
        Method = argv[2]    

    CodeGenClass = CodeGen(Exe, ObjName, AssemblyName, os.getcwd(), Ast, Method)
    CodeGenClass.CodeGen()

    if "-dbg" in argv:
        for i in LexedTokens: print(i)
        print(dumps(Ast, indent=2))

if __name__ == '__main__':
    main()
    EndTime = time() - StartTime
    if "-dbg" in argv:
        Format_Time = "\nCompiled in {:.0f} seconds and {:.0f} milliseconds".format(EndTime, (EndTime - int(EndTime)) * 1000)
        print(Format_Time, end="")
    #use echo %ERRORLEVEL% in cmd Promt 
    #use $LASTEXITCODE in vscode