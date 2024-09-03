;--Headers--
bits 64
default rel
;----Know Variables--
section .data 
    msg db "Hello, World", 13, 10
    msg_len equ $ - msg

    msg2 db "Hi", 0
    msg2_len equ $- msg2

;--Code/Text Section--
section .text
	global main
;--Imports/Extern--
extern ExitProcess
extern std_print


;--Entry Point--
main:
	mov rbx, msg
    mov r10, msg_len
    call std_print

	mov rbx, msg2
    mov r10, msg2_len
    call std_print

    mov rcx, 0
    call ExitProcess


;Zed Compiler Project 'Zedc' offical Zed Compiler
;Credits: python, gcc, nasm