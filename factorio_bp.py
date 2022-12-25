import json, base64, zlib

def encode_bp(data):
   j = json.dumps(data)
   z = zlib.compress(j.encode('utf-8'), level=9)
   b = base64.b64encode(z).decode('utf-8')
   return '0' + b

def decode_bp(bp):
   b = base64.b64decode(bp[1:])
   z = zlib.decompress(b)
   j = json.loads(z)
   return j
