#input 1000
#vram_start 900
#vmap_start 800

; load bitmap
mov wa #vmap_start
mov wd 1

mov wa #vmap_start+1
mov wd 0xFFFFFFFF

start:

; clear screen
mov a 63
mov wa #vram_start
clear:
mov wd 0 \
dec a \
jnz clear:
inc wa

; input
mov wd 1
mov a 0
mov b #vram_start-1
mov ra #input

loop:
mov ra 0
mov wa add
mov a rd \
j loop:
mov ra #input
