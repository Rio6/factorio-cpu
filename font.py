import sys
from PIL import Image, ImageFont, ImageDraw

font = ImageFont.truetype(sys.argv[1], 8)
im = Image.new('1', (8, 6))
draw = ImageDraw.Draw(im)
offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0

for i in range(ord(' '), ord('~')+1):
    c = chr(i)
    draw.rectangle([0, 0, im.width, im.height], fill='black')
    draw.text((0, offset), c, font=font, fill='white')

    bits = 0
    for b in reversed(im.tobytes()):
        bits = bits << 5 | sum(1 << (7-i) for i in range(8) if b >> i & 1)

    print(f'{bits:#010x}; {c}'.strip())
