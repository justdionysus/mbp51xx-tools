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

key = 0x3467AE81

def xor32(u,v): return (u ^ v) & 0xffffffff

def fw_scramble_type_3_inner1(b0, b4, key):
	x = fw_scramble_type_3_inner2(b4, key)
	b0, b4 = b4, xor32(b0, x)
	return (b0, b4)

def fw_scramble_type_3_inner2(x0, x4):
	x = fw_scramble_type_3_confusion(xor32(x0, x4))
	x = fw_scramble_type_3_diffusion(x)
	return x

def fw_scramble_type_3_confusion(x):
	t_f8 = 0
	t_fc = 0

	while t_fc <= 7:
		t_f4 = x & 0x0f
		t_f4 = sbox[t_fc * 16 + t_f4]
		t_f4 = ((t_f4 << 28) & 0xf0000000) & 0xffffffff

		x = x >> 4
		t_f8 = t_f8 >> 4

		t_f8 = (t_f8 | t_f4 ) & 0xffffffff

		t_fc += 1
	
	return t_f8

def fw_scramble_type_3_diffusion(x):
	t_f8 = 0
	t_fc = 0

	while t_fc <= 31:
		t_f8 |= (x >> perm[t_fc]) & 1
		t_f8 <<= 1
		t_fc += 1

	return t_f8

import sys
#print hex(fw_scramble_type_3_inner2(int(sys.argv[1], 0), key))

def descramble(f_in, f_out):
	while True:
		buff = f_in.read(8)
		if len(buff) < 8:
			f_out.write(buff)
			break

		b0, b4 = struct.unpack('<II', buff)
		b0, b4 = fw_scramble_type_3_inner1(b0, b4, key)
		buff = struct.pack('<II', b0, b4)

		f_out.write(buff)

fn_in = sys.argv[1]
fn_out = sys.argv[2]
if len(sys.argv) > 3:
	key = int(sys.argv[3], 0)

f_in = open(fn_in, 'rb')
f_out = open(fn_out, 'wb')
try:
	descramble(f_in, f_out)
finally:
	f_in.close()
	f_out.close()
