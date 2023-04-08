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

# variables
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

$debug

; show pieces
mov a 64
mov ra #pos
mov wa #disp
j memcpy:
mov z .

main:
mov ra #input
mov ra 0
noop
mov a rd

j main:
noop

memcpy:
mov wd rd \
dec a
j memcpy:
jz z
inc ra,wa

.data
bitmap:
0x01f711c4 ; king
0x01f77dd5 ; queen
0x01f728ce ; bishop
0x01f779c4 ; knight
0x01f73bf5 ; rook
0x01f73880 ; pawn
