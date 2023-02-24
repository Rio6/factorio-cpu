import sys
from getopt import getopt
from math_parser import evaluate as evalmath
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

class AssemblerError(Exception):
   def __init__(self, msg):
      self.msg = msg

   def __repr__(self):
      return self.msg

class FactorioRom:
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
               raise AssemblerError("can not merge instructions with conflicting controls")
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

   def iter_cont(self):
      for i, c in enumerate(self.controls):
         yield i + self.contoff, c

   def __repr__(self):
      return repr(self.controls) + '\n' + repr(self.romdata)

def split_words(line):
   quote = None
   escaped = False
   parsed = -1
   words = []
   line = line.strip(' \n\r\t')
   count = 0

   def int_or_str(v):
      try:
         return int(v, 0)
      except ValueError:
         return v

   for i, c in enumerate(line):
      count += 1
      if quote is not None:
         if escaped:
            escaped = False
         elif c == '\\':
            escaped = True
         elif c == quote:
            if c == "'":
               if i - parsed > 2:
                  raise AssemblerError(f"character literal {line[parsed:i+1]} too long")
               words.append(ord(line[parsed+1:i]))
            else:
               words.append(bytes(line[parsed+1:i], 'utf-8').decode("unicode_escape"))

            quote = None
            parsed = i
      else:
         if c in ['"', "'"]:
            if i - parsed > 1:
               raise AssemblerError(f"unexpected quote in {line}")
            quote = c
            parsed = i
         elif c in [' ', '\t']:
            if i - parsed > 1:
               words.append(int_or_str(line[parsed+1:i]))
            parsed = i
         elif c == ';':
            parsed = i
            break

   if count - parsed > 1:
      words.append(int_or_str(line[parsed+1:count]))

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

   factoriorom = FactorioRom(contoff=contoff, romoff=romoff)
   section = 'code'
   labels = {}
   consts = {}

   def evaluate(exp):
      return int(evalmath(
         exp,
         **labels,
         **{k: v for (k, v) in reversed(consts.items())} # reversed to fix dependency
      ))

   # convert each line to control signals
   for line in fdi:
      line = line.strip(' \n\r\t')
      words = split_words(line)
      merge_next = False

      if words and words[-1] == '\\':
         merge_next = True
         words.pop()

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
                     raise AssemblerError(f"duplicated label {label}")
                  if factoriorom.merge:
                     print("warning: label breaks up merged instructions", file=sys.stderr)
                  labels[label] = factoriorom.contraddr()

               case 'data' | _:
                  # data labels
                  if label in labels:
                     raise AssemblerError(f"duplicated label {label}")
                  labels[label] = factoriorom.romaddr()
            words = rest

      # process instruction and data
      match words:
         case ['mov', dst, src] if section == 'code':
            if type(src) is int:
               # mov immediate with literal
               factoriorom.add_control(genmov(dst, 'immed', src))
            elif src[0] == '#' or src[-1] == ':' or src == '.':
               # mov immediate with label address or constant
               factoriorom.add_control(genmov(dst, 'immed', src))
            else:
               # mov register
               factoriorom.add_control(genmov(dst, src))

         case ['inc' | 'dec' as inc, reg] if section == 'code':
            factoriorom.add_control(genmov(reg, inc))

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
                  factoriorom.add_control(genmov('jmp', 'immed', immed))
               else:
                  factoriorom.add_control(genmov('jmp', tgt))
            else:
               # jz, jnz short command
               match cond:
                  case 'z': cond = 'zero'
                  case 'nz': cond = 'nero'

               if immed is not None:
                  factoriorom.add_control(genmov('cj', cond))
                  factoriorom.add_control({'D': immed})
               else:
                  factoriorom.add_control({
                     **genmov('cj', cond),
                     **genmov('cd', tgt)
                  })
                  factoriorom.add_control({})

         case ['noop'] if section == 'code':
            factoriorom.add_control({})

         case [*values] if section == 'data':
            # rom data
            for vv in values:
               if type(vv) == str:
                  if vv[0] == '#':
                     factoriorom.add_romdata(vv) # TODO support string as constant type
                  else:
                     for v in vv:
                        factoriorom.add_romdata(ord(v))
               elif type(vv) == int:
                  factoriorom.add_romdata(vv)
               else:
                  raise AssemblerError(f"only int and string data is supported")

         case [name, value] if name and name[0] == '#':
            # constant define
            consts[name[1:]] = value

         case [] | ['']:
            pass

         case _:
            raise AssemblerError(f"error parsing {line}")

      if merge_next:
         factoriorom.merge_next()

   # populate labels, constants, rom addresses
   for addr, cont in factoriorom.iter_cont():
      d = cont.get('D')
      if type(d) == str:
         if d == '.':
            cont['D'] = addr + 1

         elif d[-1] == ':':
            if d not in labels:
               raise AssemblerError(f"unknown label {d}", file=sys.stderr)
            cont['D'] = labels[d]

         elif d[0] == '#':
            try:
               cont['D'] = evaluate(d[1:])
            except Exception:
               raise AssemblerError(f"failed to parse expression {d[1:]}")

      if d is not None:
         # make sure data are signed 32bit int
         cont['D'] = (cont['D'] + 2**31) % 2**32 - 2**31

   for i, data in enumerate(factoriorom.romdata):
      if type(data['D']) == str and len(data['D']) > 1 and data['D'][0] == '#':
         data['D'] = evaluate(data['D'][1:])

   if debug:
      fdo.write(repr(labels) + '\n')
      fdo.write(repr(factoriorom) + '\n')
   else:
      # generate blueprints for 2 roms
      controlbp = generate_rom(factoriorom.controls, start_addr=contoff, columns=10)
      romdatabp = generate_rom(factoriorom.romdata, start_addr=romoff, columns=10, entity_start=len(controlbp['blueprint']['entities'])+1)

      # merge blueprints
      for e in romdatabp['blueprint']['entities']:
         e['position']['x'] += 14
      controlbp['blueprint']['entities'] += romdatabp['blueprint']['entities']

      # print blueprint
      fdo.write(encode_bp(controlbp) + '\n')

if __name__ == '__main__':
   try:
      sys.exit(main(sys.argv))
   except AssemblerError as e:
      print(e, file=sys.stderr)
