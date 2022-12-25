import sys, json
from factorio_bp import encode_bp

print(encode_bp(json.loads(sys.stdin.read())))
