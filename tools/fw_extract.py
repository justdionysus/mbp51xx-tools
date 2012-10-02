#!/usr/bin/env python

import struct

def read(f, count):
	data = f.read(count)
	if len(data) != count:
		raise Exception('read failed to read enough bytes')
	return data

def parse_index_table(f):
	header = read(f, 0x20)
	if header[:len('index_table')] != 'index_table':
		raise('not a fw image - index_table check failed')
	entry_count = struct.unpack('<I', read(f, 4))[0]

	entries = {}
	for i in range(entry_count):
		data = read(f, 0x2c)
		name_all, offset, length, checksum = struct.unpack('<32sIII', data)
		name = name_all.split('\x00')[0]
		entries[name] = (offset, length, checksum)
	return entries


def fw_checksum(f, offset, length):
	f.seek(offset)
	t_f8 = 0
	length = length / 4
	while length != 0:
		d0, d2 = struct.unpack('<HH', f.read(4))
		t_f8 = (t_f8 + d0 + d2) & 0xffff
		length -= 1
	return t_f8


import sys
in_fn = sys.argv[1]
out_dir = sys.argv[2]

in_f = open(in_fn, 'rb')
entries = parse_index_table(in_f)
for name in entries:
	print '%s:' % (name, )
	print '  %08x %08x %08x' % entries[name]
	if name != 'index_table':
		checksum = fw_checksum(in_f, entries[name][0], entries[name][1])
		print '  computed checksum: %08x' % (checksum, )
		if checksum != entries[name][2]:
			print '  ***************** checksum doesnt match!'


def copy_chunk(inf, offset, size, outf):
	inf.seek(offset)
	while True:
		chunk = 4096
		if size < chunk:
			chunk = size
		if chunk == 0:
			break
		data = read(inf, chunk)
		outf.write(data)
		size -= chunk

import os.path
for name in entries:
	out_fn = os.path.join(out_dir, name)
	out_f = open(out_fn, 'wb')
	copy_chunk(in_f, entries[name][0], entries[name][1], out_f)
	out_f.close()


in_f.close()
