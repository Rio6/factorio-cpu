#pos 400
#vram 800
#disp 900

#bk (1 | 5<<28)
#bq (2 | 5<<28)
#bb (3 | 5<<28)
#bn (4 | 5<<28)
#br (5 | 5<<28)
#bp (6 | 5<<28)
#wk 1
#wq 2
#wb 3
#wn 4
#wr 5
#wp 6

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

end:
j end:
noop

memcpy:
dec a
jz z
noop
j memcpy: \
mov wd rd
inc ra,wa

.data
bitmap:
0x01f711c4 ; king
0x01f77dd5 ; queen
0x01f728ce ; bishop
0x01f779c4 ; knight
0x01f73bf5 ; rook
0x01f73880 ; pawn
