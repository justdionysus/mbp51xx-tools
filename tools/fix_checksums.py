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
		entry_offset = f.tell()
		data = read(f, 0x2c)
		name_all, offset, length, checksum = struct.unpack('<32sIII', data)
		name = name_all.split('\x00')[0]
		entries[name] = (offset, length, checksum, entry_offset)
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
fn = sys.argv[1]
in_f = open(fn, 'rb')
fix_u32s = []
entries = parse_index_table(in_f)
for name in entries:
	print '%s:' % (name, )
	print '  %08x %08x %08x %08x' % entries[name]
	if name != 'index_table':
		checksum = fw_checksum(in_f, entries[name][0], entries[name][1])
		print '  computed checksum: %08x' % (checksum, )
		if checksum != entries[name][2]:
			fix_u32s.append((entries[name][3] + 0x28, checksum))

print

in_f.close()
out_f = open(fn, 'r+b')
for offset, value in fix_u32s:
	print '[+] Fixing checksum @ 0x%08x -- should be 0x%08x' % (offset, value)
	out_f.seek(offset)
	out_f.write(struct.pack('<I', value))
out_f.close()
