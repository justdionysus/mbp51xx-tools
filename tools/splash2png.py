#!/usr/bin/env python

import struct
import sys
import subprocess

in_fn = sys.argv[1]
out_fn = sys.argv[2]

in_f = open(in_fn, 'rb')

out_f = open('/tmp/splash.ppm', 'w')

print >> out_f, "P3"
print >> out_f, "720 480"
print >> out_f, "255"

for y in range(480):
	for x in range(720):
		w = struct.unpack('<H', in_f.read(2))[0]
		r = (w & 0x7c00) >> 10
		g = (w & 0x03e0) >> 5
		b = (w & 0x001f)
		r <<= 3
		g <<= 3
		b <<= 3
		print >> out_f, "%d %d %d" % (r, g, b)

out_f.close()

subprocess.call("convert /tmp/splash.ppm %s" % (out_fn,), shell=True)
