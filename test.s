mov wa,wd 0
mov a 1
mov b 61

loop:
mov wa a
mov wd a
jlt loop:
inc a

end:
j end:
