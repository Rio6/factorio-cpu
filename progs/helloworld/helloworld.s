#vmap_start 800
#first_line 900
#second_line 908
#bitmap_len 95
#c0 0x20000000
#c1 0x60000000

.data
hello: "hello\0"
world: "world\0"

.code
; clear screen
mov wa #first_line
mov a 64
clear:
dec a
mov wd 0
jnz clear:
inc wa

; load bitmap
mov a 0
mov b #bitmap_len
mov ra bitmap:

; load bitmap offset
mov wa #vmap_start
mov wd ' '

; copy from rom to vmap
load_bitmap:
inc ra,wa
mov wd rd

jlt load_bitmap:
inc a

; display message
mov ra hello:
mov wa #first_line
mov b #c0

j disp_message:
mov z disp1:
disp1:

mov ra world:
mov wa #second_line
mov b #c1

j disp_message:
mov z end:

end:
j end:
noop

; ra message start
; wa line start
; b  color
; z  return address
disp_message:
mov a rd
inc ra,wa
jnz disp_message:
mov wd add
j z
noop

.data
; font generated from http://www.orgdot.com/aliasfonts/org_01.zip
bitmap:
0x00000000;
0x00100421; !
0x00000005; "
0x00afabea; #
0x01fa7cbf; $
0x01111111; %
0x0174fd2f; &
0x00000001; '
0x00208422; (
0x00110841; )
0x000288a0; *
0x00011c40; +
0x02100000; ,
0x00003c00; -
0x00100000; .
0x00111110; /
0x01f8c63f; 0
0x00108421; 1
0x01f0fe1f; 2
0x01f87e1f; 3
0x01087e31; 4
0x01f87c3f; 5
0x01f8fc3f; 6
0x0108421f; 7
0x01f8fe3f; 8
0x01f87e3f; 9
0x00100020; :
0x00108020; ;
0x00410444; <
0x000781e0; =
0x00111041; >
0x0040721f; ?
0x01f0f6bf; @
0x0118fe3f; A
0x00f8be2f; B
0x01f0843f; C
0x00f8c62f; D
0x01f0fc3f; E
0x0010fc3f; F
0x01f8f43f; G
0x0118fe31; H
0x01f2109f; I
0x01f4a11e; J
0x01168db1; K
0x01f08421; L
0x015ad6bf; M
0x0118c63f; N
0x01f8c63f; O
0x0010fe3f; P
0x01fcc63f; Q
0x0094fe3f; R
0x01f87c3f; S
0x0042109f; T
0x01f8c631; U
0x00454631; V
0x01fad6b5; W
0x01151151; X
0x00422a31; Y
0x01f0fe1f; Z
0x00308423; [
0x01041041; \
0x00310843; ]
0x000000a2; ^
0x3e000000; _
0x00000001; `
0x00f7a1e0; a
0x00f4a5e1; b
0x00f085e0; c
0x00f4a5e8; d
0x00f0bde0; e
0x00211c46; f
0x10f4a5e0; g
0x0094a5e1; h
0x00108420; i
0x06210840; j
0x0094bca1; k
0x00108421; l
0x0118d7e0; m
0x0094a5e0; n
0x00f4a5e0; o
0x02f4a5e0; p
0x08f4a5e0; q
0x001085e0; r
0x00f43840; s
0x004213e4; t
0x00f4a520; u
0x00e4a520; v
0x01fac620; w
0x00931920; x
0x10f4a520; y
0x00f09c80; z
0x00410c44; {
0x00108421; |
0x00111841; }
0x0000fe00; ~
