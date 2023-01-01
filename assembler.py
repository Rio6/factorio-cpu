import sys
from getopt import getopt
from rom import generate_rom
from factorio_bp import encode_bp

src_regs = {
   'dec'   : -2,
   'inc'   : -1,
   'immed' : 1,
   'rd'    : 2,
   'add'   : -3,
   'sub'   : 4,
   'mul'   : 5,
   'div'   : 6,
   'mod'   : 7,
   'exp'   : 8,
   'ls'    : 9,
   'rs'    : 10,
   'and'   : 11,
   'or'    : 12,
   'xor'   : 13,
   'eq'    : 14,
   'ne'    : 15,
   'lt'    : 16,
   'gt'    : 17,
   'le'    : 18,
   'ge'    : 19,
   'zero'  : 20,
   'nero'  : 21,
   'a'     : 22,
   'b'     : 23,
   'x'     : 24,
   'y'     : 25,
   'z'     : 26,
}

dst_regs = {
   'a': 'A',
   'b': 'B',
   'x': 'X',
   'y': 'Y',
   'z': 'Z',
   'jmp': 'J',
   'cj': 'K',
   'cd': 'C',
   'ra': 'R',
   'wa': 'W',
   'wd': 'L',
}

class Parser:
   def __init__(self, *args, contoff=1, romoff=1):
      self.controls = []
      self.romdata = []
      self.contoff = contoff
      self.romoff = romoff
      self.merge = False;

   def add_control(self, control):
      if self.merge and len(self.controls) > 0:
         for k, v in control.items():
            if k in self.controls[-1].keys() and self.controls[-1][k] != v:
               raise ValueError("can not merge instructions with conflicting controls")
         self.controls[-1].update(control)
      else:
         self.controls.append(control)
      self.merge = False

   def add_romdata(self, romdata):
      self.romdata.append({'D': romdata})

   def merge_next(self):
      self.merge = True

   def contraddr(self):
      return len(self.controls) + self.contoff

   def romaddr(self):
      return len(self.romdata) + self.romoff

   def __repr__(self):
      return repr(self.controls) + '\n' + repr(self.romdata)

def split_words(line):
   quote = None
   escaped = False
   parsed = -1
   words = []
   line = line.strip(' \n\r\t\\')

   def try_int(v):
      try:
         return int(v, 0)
      except ValueError:
         return v

   for i, c in enumerate(line):
      if quote is not None:
         if escaped:
            escaped = False
         elif c == '\\':
            escaped = True
         elif c == quote:
            if c == "'":
               if i - parsed > 2:
                  raise ValueError(f"character literal {line[parsed:i+1]} too long")
               words.append(ord(line[parsed+1:i]))
            else:
               words.append(bytes(line[parsed+1:i], 'utf-8').decode("unicode_escape"))

            quote = None
            parsed = i
      else:
         if c in ['"', "'"]:
            if i - parsed > 1:
               raise ValueError(f"unexpected quote in {line}")
            quote = c
            parsed = i
         elif c in [' ', '\t']:
            if i - parsed > 1:
               words.append(try_int(line[parsed+1:i]))
            parsed = i

   if len(line) - parsed > 1:
      words.append(try_int(line[parsed+1:len(line)]))

   return words

def genmov(dst, src, data=None):
   dst = dst.lower().split(',')
   src = src.lower()
   if data is not None:
      return {**{dst_regs[d]: src_regs[src] for d in dst}, 'D': data}
   else:
      return {dst_regs[d]: src_regs[src] for d in dst}

def nonempty_str(s):
   return type(s) is str and len(s) > 0

def main(args):
   fdi = sys.stdin
   fdo = sys.stdout
   debug = False
   contoff = 1
   romoff = 1

   for [k, v] in getopt(args[1:], 'i:o:s:d')[0]:
      match k:
         case '-i':
            fdi = open(v, 'r')
         case '-o':
            fdo = open(v, 'w')
         case '-s':
            romoff = int(v)
         case '-d':
            debug = True

   parser = Parser(contoff=contoff, romoff=romoff)
   section = 'code'
   labels = {}
   consts = {}

   # convert each line to control signals
   for line in fdi:
      line = line.strip(' \n\r\t')
      code = line.split(';')[0]
      words = split_words(code)
      merge_next = '\\' in code

      # process section directives and labels
      match words:
         case [sec] if nonempty_str(sec) and sec[0] == '.':
            section = sec[1:]
            words = []

         case [label, *rest] if nonempty_str(label) and label[-1] == ':':
            match section:
               case 'code':
                  # code labels
                  if label in labels:
                     raise ValueError(f"duplicated label {label}")
                  labels[label] = parser.contraddr()

               case 'data' | _:
                  # data labels
                  if label in labels:
                     raise ValueError(f"duplicated label {label}")
                  labels[label] = parser.romaddr()
            words = rest

      # process instruction and data
      match words:
         case ['mov', dst, src] if section == 'code':
            if type(src) is int:
               # mov immediate with literal
               parser.add_control(genmov(dst, 'immed', src))
            elif src[0] == '#' or src[-1] == ':':
               # mov immediate with label address or constant
               parser.add_control(genmov(dst, 'immed', src))
            else:
               # mov register
               parser.add_control(genmov(dst, src))

         case ['inc' | 'dec' as inc, reg] if section == 'code':
            parser.add_control(genmov(reg, inc))

         case [j, tgt] if section == 'code' and j[0] == 'j':
            cond = j[1:]

            if type(tgt) is int:
               # jump to immediate
               immed = tgt
            elif tgt[-1] == ':':
               # jump to label, use as place holder and set values later
               immed = tgt
            else:
               # jump to register
               immed = None

            if not cond:
               if immed is not None:
                  parser.add_control(genmov('jmp', 'immed', immed))
               else:
                  parser.add_control(genmov('jmp', tgt))
            else:
               # jz, jnz short command
               match cond:
                  case 'z': cond = 'zero'
                  case 'nz': cond = 'nero'

               if immed is not None:
                  parser.add_control(genmov('cj', cond))
                  parser.add_control({'D': immed})
               else:
                  parser.add_control({
                     **genmov('cj', cond),
                     **genmov('cd', tgt)
                  })
                  parser.add_control({})

         case ['noop'] if section == 'code':
            parser.add_control({})

         case [*values] if section == 'data':
            # rom data
            for vv in values:
               if type(vv) == str:
                  for v in vv:
                     parser.add_romdata(ord(v))
               elif type(vv) == int:
                  parser.add_romdata(vv)
               else:
                  raise ValueError(f"only int and string data is supported")

         case [name, value] if name and name[0] == '#':
            # constant define
            if type(value) is not int:
               raise ValueError(f"constant must be integer, got {value}")
            consts[name] = value

         case [] | ['']:
            pass

         case _:
            raise ValueError(f"error parsing {line}")

      if merge_next:
         parser.merge_next()

   # populate labels, constants, rom addresses
   for cont in parser.controls:
      d = cont.get('D')
      if type(d) == str:
         if d[-1] == ':':
            if d not in labels:
               print(f"unknown label {d}", file=sys.stderr)
               return 1
            cont['D'] = labels[d]

         if d[0] == '#':
            if d not in consts:
               print(f"unknown constant {d}", file=sys.stderr)
               return 1
            cont['D'] = consts[d]

   if debug:
      fdo.write(repr(labels) + '\n')
      fdo.write(repr(parser) + '\n')
   else:
      # generate blueprints for 2 roms
      controlbp = generate_rom(parser.controls, start_addr=contoff, columns=10)
      romdatabp = generate_rom(parser.romdata, start_addr=romoff, columns=10, entity_start=len(controlbp['blueprint']['entities'])+1)

      # merge blueprints
      for e in romdatabp['blueprint']['entities']:
         e['position']['x'] += 14
      controlbp['blueprint']['entities'] += romdatabp['blueprint']['entities']

      # print blueprint
      fdo.write(encode_bp(controlbp) + '\n')

if __name__ == '__main__':
   try:
      sys.exit(main(sys.argv))
   except ValueError as e:
      print(e, file=sys.stderr)
