import sys, json
from factorio_bp import decode_bp

print(json.dumps(decode_bp(sys.stdin.read())))
