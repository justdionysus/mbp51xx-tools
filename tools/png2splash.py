#!/usr/bin/env python

import sys
import subprocess
import struct

# Convert rgb888 to rgb555
def rgb888_to_rgb555(in_f, out_f):
	while True:
		pdata = in_f.read(3)
		if len(pdata) != 3: break
		r, g, b = struct.unpack("<BBB", pdata)
		r = min(int(round(float(r) / 8.0)), 31)
		g = min(int(round(float(g) / 8.0)), 31)
		b = min(int(round(float(b) / 8.0)), 31)
		p = 0x8000 | (r << 10) | (g << 5) | b
		pdata = struct.pack('<H', p)
		out_f.write(pdata)

 
# Convert image to raw RGB555
def image_to_rgb555(in_fn, out_fn):
	subprocess.call("convert %s -depth 8 -resize 720x480! rgb:/tmp/splash888.raw" % (in_fn,), shell=True)

	f = open("/tmp/splash888.raw", "rb")
	out_f = open(out_fn, "wb")
	rgb888_to_rgb555(f, out_f)
	out_f.close()
	f.close()

def main():
	image_fn = sys.argv[1]
	splash_fn = sys.argv[2]
	image_to_rgb555(image_fn, splash_fn)

main()


