import re

pieces = ['king', 'queen', 'bishop', 'knight', 'rook', 'pawn']
rows = []

for piece in pieces:
   with open(f'{piece}.xbm') as fd:
      xbm = fd.read()

   bits = 0
   for row in reversed(re.findall(r'0x[a-fA-F0-9]+', xbm)):
      row = int(row, 16)
      bits = (bits << 5) | row

   rows.append(bits)

for i, row in enumerate(rows):
   print(f'0x{row:08x} ; {pieces[i]}')
