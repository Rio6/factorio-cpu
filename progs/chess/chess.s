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

mov ra #input ; read from input
mov ra 0      ; clear read register
noop          ; wait for input
mov a,y rd    ; save user input, check zero
mov a x       ; check saved value is not zero
jz loop:      ; input is zero, skip
noop

jnz sel_fin:  ; jump using saved value
noop

j loop:       ; saved value is zero
mov x y       ; save input value

sel_fin:      ; saved value is not zero
j move_piece: ; move piece
mov z .
j loop:       ; loop
mov x 0       ; clear saved value

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
move_piece:
mov a x         ; calculate source address
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

mov wa add      ; write piece to display destination
mov wd x

j z             ; return
noop

.data
bitmap:
0x01f711c4 ; king
0x01f77dd5 ; queen
0x01f728ce ; bishop
0x01f779c4 ; knight
0x01f73bf5 ; rook
0x01f73880 ; pawn
