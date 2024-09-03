;--Headers--
bits 64
default rel
;----Know Variables--
section .data
;--Code/Text Section--
section .text
	global main
;--Imports/Extern--
extern ExitProcess
;--Entry Point--
main:
    sub rsp, 48
	push 1
    push 4
    push 5
    call Add
    add rsp, 24
    push rax

    push 10
    push 5
    push 0
    call Sub
    add rsp, 24
    push rax

    pop rbx
    pop rax
    add rax, rbx
    push rax



    pop rcx
    call ExitProcess

Add:
    push rbp
    mov rbp, rsp
    sub rsp, 32 

    mov rax, [rbp+32]
    push rax

    pop rax
    mov [rbp-8], rax

    mov rax, [rbp+24]
    push rax

    pop rax
    mov [rbp-16], rax

    mov rax, [rbp+16]
    push rax

    pop rax
    mov [rbp-24], rax

    mov rax, [rbp-8]
    push rax

    mov rax, [rbp-16]
    push rax

    mov rax, [rbp-24]
    push rax

    pop rbx
    pop rax
    add rax, rbx
    push rax

    pop rbx
    pop rax
    add rax, rbx
    push rax

    pop rax
    mov [rbp-32], rax

    mov rax, [rbp-32]
    push rax

    pop rax
    

    mov rsp, rbp
    pop rbp
    ret


Sub:
    push rbp
    mov rbp, rsp
    sub rsp, 32 

    mov rax, [rbp+32]
    push rax

    pop rax
    mov [rbp-8], rax

    mov rax, [rbp+24]
    push rax

    pop rax
    mov [rbp-16], rax

    mov rax, [rbp+16]
    push rax

    pop rax
    mov [rbp-24], rax

    mov rax, [rbp-8]
    push rax

    mov rax, [rbp-16]
    push rax

    mov rax, [rbp-24]
    push rax

    pop rbx
    pop rax
    sub rax, rbx
    push rax

    pop rbx
    pop rax
    sub rax, rbx
    push rax

    pop rax
    mov [rbp-32], rax

    mov rax, [rbp-32]
    push rax

    pop rax
    

    mov rsp, rbp
    pop rbp
    ret

;Zed Compiler Project 'Zedc' offical Zed Compiler
;Credits: python, gcc, nasm