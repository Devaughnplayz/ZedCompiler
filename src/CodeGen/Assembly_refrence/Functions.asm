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
	mov rax, 40
	mov rbx, 20

	sub rsp, 16
	mov [rsp + 8], rax
	mov [rsp], rbx

	mov rcx, [rsp]
	call AddFunc

	add rsp, 16

	call ExitProcess
AddFunc:

	mov rbx, [rsp + 16]
	mov rax, [rsp + 8]

	add rax, rbx
	mov rcx, rax

	ret