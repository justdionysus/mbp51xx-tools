#!/usr/bin/env python

import sys
import struct
import os.path

partitions = {
		'fma3': (0x00f80000, 0x00040000),
		'fma4': (0x00fc0000, 0x003a0000),
		'fma5': (0x01360000, 0x00e00000),
		'fma6': (0x02160000, 0x00a80000),
		'fma7': (0x02be0000, 0x00dc0000),
		#'splash1': (0x
	}

def read(f, count):
	data = f.read(count)
	if len(data) != count:
		raise Exception('read failed to read enough bytes')
	return data

def copy_chunk(inf, offset, size, outf):
	print 'copy_chunk(..., %08x, %08x, ...)' % (offset, size)
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

in_fn = sys.argv[1]
out_dir = sys.argv[2]

in_f = open(in_fn, 'rb')
fw_entry_name = read(in_f, 0x20)
assert(fw_entry_name.startswith('nand_rom_cmpr'))
unk, entry_count, length = struct.unpack('<III', in_f.read(12))
entries = []
for i in range(entry_count):
	entry = struct.unpack('<III', in_f.read(12))
	entries.append(entry)

file_offset = in_f.tell()
nand_offset = 0
for idx, entry in enumerate(entries):
	size, typ, unk = entry
        if typ == 0:
		print 'NAND: [0x%08x, 0x%08x) @ 0x%08x' % (nand_offset, nand_offset + size, file_offset)

		for name in partitions:
			p_offset, p_size = partitions[name]
			if p_offset >= nand_offset and p_offset < (nand_offset + size):
				f_offset = file_offset + (p_offset - nand_offset)
				f_size = min(size - (p_offset - nand_offset), p_size)

				out_fn = os.path.join(out_dir, name)
				out_f = open(out_fn, 'wb')
				copy_chunk(in_f, f_offset, f_size, out_f)
				out_f.close()

		file_offset += size
	nand_offset += size

in_f.close()
