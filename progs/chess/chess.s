; memory locations
#vram 800
#disp 900
#input 1000

; colour
#pink (5 << 28)

; chess piece definitions
#bk (1 | pink)
#bq (2 | pink)
#bb (3 | pink)
#bn (4 | pink)
#br (5 | pink)
#bp (6 | pink)
#wk 1
#wq 2
#wb 3
#wn 4
#wr 5
#wp 6

; variables
#pos 400
#selected 432

.data
initial:
#br #bn #bb #bq #bk #bb #bn #br
#bp #bp #bp #bp #bp #bp #bp #bp
0   0   0   0   0   0   0   0
0   0   0   0   0   0   0   0
0   0   0   0   0   0   0   0
0   0   0   0   0   0   0   0
#wp #wp #wp #wp #wp #wp #wp #wp
#wr #wn #wb #wq #wk #wb #wn #wr

.code
; move bitmaps to vram
mov a 12
mov ra bitmap:
mov wa #vram+1
j memcpy:
mov z .

mov wa #vram
mov wd 1

; move initial position to ram
mov a 64
mov ra initial:
mov wa #pos
j memcpy:
mov z .

; show pieces
mov a 64
mov ra #pos
mov wa #disp
j memcpy:
mov z .

loop:

mov ra #input   ; read from input
mov ra 0        ; clear read register
mov b #pos-1    ; calculate selected address
mov a,y rd      ; save user input, check zero
mov a x \       ; check saved value is not zero
mov ra add      ; address of selected position
jz loop:        ; input is zero, skip
mov a rd        ; read value of selected position

jnz check_move: ; check if saved value is zero
mov z sel_fin:  ; go to sel_fin when returning from check_move

; saved value is zero
jz loop:        ; if selected position is empty, continue
noop

j loop:         ; else
mov x y         ; save input value

sel_fin:        ; saved value is not zero
noop            ; wait for jnz condition

jnz move_piece: ; move piece if valid
mov z .

j loop:         ; loop
mov x 0         ; clear saved value

; a count
; ra src
; wa dst (set right before j)
memcpy:
mov wd rd \
jz z
dec a
j memcpy: \
inc ra
inc wa

; x src
; y dst
; a 1 if valid, 0 if not
; checks for colour only
check_move:
mov b #pos-1 \  ; calculate addresses
mov a y         ; dest address
mov ra add \    ; read dest value
mov a x         ; source address
mov ra add      ; read source value
mov a rd        ; store dest value to a
mov b rd        ; store source value to b

jz z            ; pass if dest has no piece
mov a 1         ; return 1

mov a xor \     ; check colour bits
mov b 0x7FFFFFF
noop            ; wait for calculation
noop

jle z           ; same colour, fail
mov a 0         ; return 0

j z
mov a 1         ; return 1

; x src
; y dst
; move the piece and update display
move_piece:
mov a x \       ; calculate source address
mov b #pos-1

mov ra,wa add \ ; read write from source
mov a y         ; calculate destination address

mov wd 0 \      ; write 0 to source
mov wa add      ; write to destination

mov wd,x rd \   ; read piece from source and write to destination
mov wa 0 \
mov a x         ; calculate display source address
mov b #disp-1

mov a y \       ; calculate display destination address
mov wa add      ; clear source cell
mov wd 0

mov wa add      ; write to display destination
j z             ; return
mov wd x        ; write piece

.data
bitmap:
0x01f711c4 ; king
0x01f77dd5 ; queen
0x01f728ce ; bishop
0x01f779c4 ; knight
0x01f73bf5 ; rook
0x01f73880 ; pawn
