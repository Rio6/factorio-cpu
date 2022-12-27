#ram_size 61
#ram_start 801
.message "hello,\nworld\0"

mov a,wd 1
mov wa #ram_start
mov b #ram_size

mov z .message

loop:
inc wa,a \
jlt loop:
inc wd

end:
j end:
