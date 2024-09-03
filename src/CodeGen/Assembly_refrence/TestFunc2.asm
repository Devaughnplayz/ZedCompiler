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
	push rbp
	mov rbp, rsp
	sub rsp, 0


	;Pushes A Number
	push 0
	;Pushes A Number
	push 0
	;Pushes A Number
	push 0
	;jump to new program
	jmp main_1
Add_0:
	;Get argument 1
	push rbp
	mov rbp, rsp
	sub rsp, 32

	mov rax, [rbp+16]
	;Store the Argument y
	mov qword [rbp-8], rax
	;Get argument 1
	mov rax, [rbp+24]
	;Store the Argument x
	mov qword [rbp-16], rax
	;Get argument 1
	mov rax, [rbp+32]
	;Store the Argument r
	mov qword [rbp-24], rax
	;call Variable 'y'
	mov rax, [rbp-8]
	push rax
	;call Variable 'x'
	mov rax, [rbp-16]
	push rax
	pop rbx
	pop rax
	;Adds The Numbers Together
	add rax, rbx
	push rax
	;saves the variable 'results'
	pop rax
	mov qword [rbp-32], rax
	;call Variable 'results'
	mov rax, [rbp-32]
	push rax
	;call Variable 'r'
	mov rax, [rbp-24]
	push rax
	pop rbx
	pop rax
	;Adds The Numbers Together
	add rax, rbx
	push rax
	;Moves new value into the variable
	pop rax
	mov qword [rbp-32], rax
	mov rax, [rbp-32]
	push rax
	;call Variable 'results'
	mov rax, [rbp-32]
	push rax
	;Returns from function
	pop rax
	;Cleans up frame to return
	add rsp, 24
	mov rsp, rbp
	pop rbp
	ret
	add rsp, 24
	
	mov rsp, rbp
	pop rbp

	mov rax, 0
	ret
main_1:
	;Pushes A Number
	push 0
	;Pushes A Number
	push 0
	;Pushes A Number
	push 0
	;jump to new program
	jmp main_2
Sub_0:
	;Get argument 1
	push rbp
	mov rbp, rsp
	sub rsp, 32

	mov rax, [rbp+16]
	;Store the Argument y
	mov qword [rbp-8], rax
	;Get argument 1
	mov rax, [rbp+24]
	;Store the Argument x
	mov qword [rbp-16], rax
	;Get argument 1
	mov rax, [rbp+32]
	;Store the Argument r
	mov qword [rbp-24], rax
	;call Variable 'y'
	mov rax, [rbp-8]
	push rax
	;call Variable 'x'
	mov rax, [rbp-16]
	push rax
	pop rbx
	pop rax
	;Subtracts The Numbers Together
	sub rax, rbx
	push rax
	;saves the variable 'results'
	pop rax
	mov qword [rbp-32], rax
	;call Variable 'results'
	mov rax, [rbp-32]
	push rax
	;call Variable 'r'
	mov rax, [rbp-24]
	push rax
	pop rbx
	pop rax
	;Adds The Numbers Together
	add rax, rbx
	push rax
	;Moves new value into the variable
	pop rax
	mov qword [rbp-32], rax
	mov rax, [rbp-32]
	push rax
	;call Variable 'results'
	mov rax, [rbp-32]
	push rax
	;Returns from function
	pop rax
	;Cleans up frame to return
	add rsp, 24
	mov rsp, rbp
	pop rbp
	ret
	add rsp, 24
	
	mov rsp, rbp
	pop rbp

	mov rax, 0
	ret
main_2:
	;Pushes A Number
	push 1
	;Pushes A Number
	push 4
	;Pushes A Number
	push 5
	;call function Add
	call Add_0
	;push return val
	push rax
	;Pushes A Number
	push 10
	;Pushes A Number
	push 5
	;Pushes A Number
	push 0
	;call function Sub
	call Sub_0
	;push return val
	push rax
	pop rbx
	pop rax
	;Adds The Numbers Together
	add rax, rbx
	push rax
	;Exits The Program
	pop rcx
	call ExitProcess
	
	
	mov rsp, rbp
	pop rbp

	;Main Exit Program
	mov rcx, 0
	call ExitProcess


;Zed Compiler Project 'Zedc' offical Zed Compiler
;Credits: python, gcc, nasm