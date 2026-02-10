import struct
import sys
import datetime
import os
import zlib
import argparse


class UpgParser:
    # Based on pkg_hd_str: name[128], soft_desc[64], soft_sn[64], version[32], build_time[Q], psize[Q], img_num[I], img_w_mode[I], hd_crc32[I]
    PKG_HD_FMT = "<128s64s64s32sQQIII"
    PKG_HD_SIZE = struct.calcsize(PKG_HD_FMT)

    # Based on img_nd_str: img_name[128], partition[64], size[Q], offset[Q], write_offset[Q], img_crc32[I], no_crc32[I]
    IMG_ND_FMT = "<128s64sQQQII"
    IMG_ND_SIZE = struct.calcsize(IMG_ND_FMT)

    def __init__(self, args):
        self.args = args

    def decode_str(self, raw_bytes):
        return raw_bytes.split(b'\x00')[0].decode('utf-8', errors='replace')

    def calculate_crc32(self, path):
        crc = 0
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                crc = zlib.crc32(chunk, crc)
        return crc & 0xFFFFFFFF

    def process(self):
        if not os.path.exists(self.args.input):
            print(f"File not found: {self.args.input}")
            return

        try:
            with open(self.args.input, 'rb') as f:
                # 1. Parse Package Header
                header_data = f.read(self.PKG_HD_SIZE)
                if len(header_data) < self.PKG_HD_SIZE:
                    return

                (name, desc, sn, ver, btime, psize, img_num, wmode, hcrc) = \
                    struct.unpack(self.PKG_HD_FMT, header_data)

                dt = datetime.datetime.fromtimestamp(btime)

                print(f"# Package name:  {self.decode_str(name)}")
                print(f"    Build time:  {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"    Size:        {psize:x} ({psize}B {psize / (1024 * 1024):.2f}MB)")
                print(f"    Image num:   {img_num}")
                print(f"    Write mode:  {wmode}")
                print(f"    Version:     {self.decode_str(ver)}")
                print(f"    Serial num:  {self.decode_str(sn)}")
                print(f"    Desc:        {self.decode_str(desc)}")
                print(f"    Head crc32:  {hcrc:X}\n")

                # 2. Parse Image Nodes
                for i in range(img_num):
                    node_data = f.read(self.IMG_ND_SIZE)
                    if not node_data: break

                    (iname, ipart, isize, ioffs, iw_offs, icrc, ncrc) = \
                        struct.unpack(self.IMG_ND_FMT, node_data)

                    img_name = self.decode_str(iname)
                    print(f"# Node image:   {img_name}")
                    print(f"    Partition:  {self.decode_str(ipart)}")
                    print(f"    Size:       {isize:x} ({isize}B {isize / (1024 * 1024):.2f}MB)")
                    print(f"    Offset:     {ioffs:x} ({ioffs})")
                    print(f"    W_ofs:      {iw_offs:x} ({iw_offs})")
                    print(f"    Imgcrc32:   {icrc:X}")
                    print(f"    Node crc32: {ncrc:X}\n")

                    if self.args.extract and isize > 0:
                        self.extract_node(f, img_name, ioffs, isize, icrc)

        except Exception as e:
            print(f"Error: {e}")

    def extract_node(self, f, name, offset, size, expected_crc):
        if not os.path.exists(self.args.output):
            os.makedirs(self.args.output)

        clean_name = "".join([c for c in name if c.isalnum() or c in ('.', '_')]).strip()
        target_path = os.path.join(self.args.output, clean_name)

        saved_pos = f.tell()
        f.seek(offset)

        with open(target_path, 'wb') as out_f:
            remaining = size
            while remaining > 0:
                chunk = f.read(min(remaining, 1024 * 1024))
                if not chunk: break
                out_f.write(chunk)
                remaining -= len(chunk)

        actual_crc = self.calculate_crc32(target_path)
        status = "OK" if actual_crc == expected_crc else "FAILED"
        print(f"    [Extraction: {target_path} - {status}]")
        f.seek(saved_pos)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UPG Firmware Tool")
    parser.add_argument("input", help="Path to the .img file")
    parser.add_argument("-x", "--extract", action="store_true", help="Extract nodes")
    parser.add_argument("-o", "--output", default="extracted_nodes", help="Output directory")

    args = parser.parse_args()
    UpgParser(args).process()