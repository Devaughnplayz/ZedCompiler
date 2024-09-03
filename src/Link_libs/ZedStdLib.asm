section .text
    global std_print
	global std_print_int
	global std_list_int
extern GetStdHandle
extern WriteFile
extern ExitProcess
extern ReadConsoleInputA

std_print:
	push rbp
	mov rbp, rsp
    ;intructions
    ;Load the message into rbx eg mov rbx, msg
    ;Load the string Lenght into r10 eg mov r10, msg.len
	sub rsp, 48h
	mov rcx, -11
	call GetStdHandle
	
	mov rcx, rax
	lea rdx, [rbx]
	mov r8d, r10d
	lea r9, [rsp+48]
	mov qword [rsp + 32], 0
	call WriteFile
	
	add rsp, 48h
	mov rsp, rbp
	pop rbp
	ret

std_list_int:
	;Buffer rsi
	;Index rcx
	;Value rax
	mov r9, 0
	cmp rcx, r9
	je .Zero_case
	mov [rsi + rcx*8], rax
	ret
.Zero_case:
	mov [rsi], rax
	ret

std_print_int:
	push rbp
	mov rbp, rsp
	sub rsp, 48h
	
	xor rcx, rcx
	mov rbx, 10
	mov rdi, rsi

get_div:
	xor rdx, rdx
	div rbx
	add dl, '0'
	mov [rsi], dl
	inc rsi
	inc rcx
	test rax, rax
	jnz get_div

reverse_str:
	dec rsi
	mov rbx, rdi
	mov rdx, rcx

swap:
	mov al, [rdi]
	mov bl, [rsi]
	mov [rsi], al
	mov [rdi], bl
	inc rdi
	dec rsi
	cmp rdi, rsi
	jl swap
	add rsp, 48h
	mov rsp, rbp
	pop rbp

	ret

std_input:
	;intustions
	;Load the String Storage in rbx
	;Outputs Meaage Len In Rax

std_error:
	ret	

std_concat:
	ret

std_argv:
	ret

std_argc:
	ret

std_vector:
	ret

std_Map:
	ret

std_alloc:
	ret

std_free:
	ret

std_int_str:
	ret