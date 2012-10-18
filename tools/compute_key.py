#!/usr/bin/env python

import struct

sbox = \
  [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15, 
   13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9, 
   10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4, 
   3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14, 
   2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9, 
   14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6, 
   4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14, 
   11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]

perm = \
  [16, 7, 20, 21, 29, 12, 28, 17, 1, 15, 23, 26, 5, 18, 31, 10, 
   2, 8, 24, 14, 0, 27, 3, 9, 19, 13, 30, 6, 22, 11, 4, 25]

def xor32(u,v): return (u ^ v) & 0xffffffff

def unconfuse(x):
	res = 0
	for i in range(8):
		curr_sbox = sbox[i * 16: i * 16 + 16]
		curr_x = x & 0x0f
 		curr_res = curr_sbox.index(curr_x)
		curr_res = curr_res << 28
		res >>= 4
		res = res | curr_res
		x >>= 4
	return res

def undiffuse(x):
	x >>= 1
	x1 = x
	x2 = x | 0x80000000
	x1 &= 0xffffffff
	x2 &= 0xffffffff

	def ud(a):
		res = 0
		for i in range(32):
			res |= ((a & 1) << perm[31 - i]) & 0xffffffff
			a >>= 1
			a &= 0xffffffff
		return res

	return (ud(x1), ud(x2))



import sys
usage = """
Example usage:

$ hexdump -C ~/projects/bluray/firmware/E5S20UD/E5S20UD1019FA1.bin | head
00000000  26 0b 93 c7 69 6e 64 65  16 cf ce a0 62 6c 65 00  |&...inde....ble.|

$ ./compute_key.py 0xc7930b26 0x65646e69 0x61745f78

"""

ct = int(sys.argv[1], 0)
pt0 = 0x65646e69
pt4 = 0x61745f78
if len(sys.argv) == 4:
	pt0 = int(sys.argv[2], 0)
	pt4 = int(sys.argv[3], 0)
elif len(sys.argv) != 2:
	print usage
	sys.exit(-1)

ud1, ud2 = undiffuse(xor32(ct, pt4))
print hex(xor32(unconfuse(ud1), pt0))
print hex(xor32(unconfuse(ud2), pt0))
sys.exit(0)
