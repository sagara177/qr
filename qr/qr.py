#!/usr/bin/env python

import argparse
import os
import os.path
import qrcode
import sys
import tempfile

from argparse import RawDescriptionHelpFormatter
from binascii import b2a_hex
from struct import *


# http://www.qrcode.com/en/about/version.html
QR_40_L_MAX_ALPHANUMERIC_BYTES = 4296
QR_40_L_MAX_BINARY_BYTES = 2953

IMAGE_PREFIX = 'qr'


def encode_hex(data_file):
    hex_filename = tempfile.mkstemp()[1]
    with open(data_file, 'rb') as fin:
        with open(hex_filename, 'w') as fout:
            fout.write(b2a_hex(fin.read()).upper())
    return hex_filename


def qr_save(filepath, data):
    qr = qrcode.QRCode(
        version=40,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data, optimize=0)
    qr.make(fit=True)

    img = qr.make_image()
    img.save(filepath)


def qr_large_file_save(data_file, split_size, output_dir):
    with open(data_file, 'rb') as f:
        index = 0
        data = f.read(split_size)
        while data:
            # generate
            image_path = '%s/%s_%06d.png' % (
                output_dir, IMAGE_PREFIX, index)
            qr_save(image_path, data)

            index += 1
            data = f.read(split_size)


def main():
    description = '''Generate QR images. Large file is being splitted.

* How to join splitted files (files: qr-000001.txt qr-000002.txt ..):
  Windows: copy /b qr-*.txt outfile
  UNIX: cat qr-*.txt > outfile

* How to decode:
  Windows: certutil -decodehex infile outfile
  UNIX: cat qr-*.txt | perl -e 'print pack "H*", <STDIN>' > outfile
'''
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('--output-dir', dest='output_dir',
                        action='store', default='./out',
                        help='QR output directory (default: ./out)')
    parser.add_argument('--hex', action='store_true', default=False,
                        help='encode with hex (for most QR readers, which \
                        do not support to save the binary data.)')
    parser.add_argument('file', type=str, help='data file')
    args = parser.parse_args()
    output_dir = args.output_dir
    hex = args.hex
    data_file = args.file

    # creates output directory if not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # maximum size using an binary character type
        split_size = QR_40_L_MAX_BINARY_BYTES

        # hex encode if option specified
        encoded_file = None
        if hex:
            encoded_file = encode_hex(data_file)
            data_file = encoded_file
            # QR Alphanumeric characters can include hex ones
            split_size = QR_40_L_MAX_ALPHANUMERIC_BYTES

        # generate QR images
        qr_large_file_save(data_file, split_size, output_dir)
    except:
        if encoded_file is not None and os.path.exists(encoded_file):
            os.remove(encoded_file)
        raise
        
    sys.exit(0)


if __name__ == "__main__":
    main()
