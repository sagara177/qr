#!/usr/bin/env python

import argparse
import os
import os.path
import qrcode
import sys
import tempfile

from argparse import RawDescriptionHelpFormatter
from binascii import b2a_hex


# http://www.qrcode.com/en/about/version.html
QR_L_MAX_BYTES = (      
    # (alphanumeric, binary)
    (  25,   17),   # version  1 ( 21x 21)
    (  47,   32),   # version  2 ( 25x 25)
    (  77,   53),   # version  3 ( 29x 29)
    ( 114,   78),   # version  4 ( 33x 33)
    ( 154,  106),   # version  5 ( 37x 37)
    ( 195,  134),   # version  6 ( 41x 41)
    ( 224,  154),   # version  7 ( 45x 45)
    ( 279,  192),   # version  8 ( 49x 49)
    ( 335,  230),   # version  9 ( 53x 53)
    ( 395,  271),   # version 10 ( 57x 57)
    ( 468,  321),   # version 11 ( 61x 61)
    ( 535,  367),   # version 12 ( 65x 65)
    ( 619,  425),   # version 13 ( 69x 69)
    ( 667,  458),   # version 14 ( 73x 73)
    ( 758,  520),   # version 15 ( 77x 77)
    ( 854,  586),   # version 16 ( 81x 81)
    ( 938,  644),   # version 17 ( 85x 85)
    (1046,  718),   # version 18 ( 89x 89)
    (1153,  792),   # version 19 ( 93x 93)
    (1249,  858),   # version 20 ( 97x 97)
    (1352,  929),   # version 21 (101x101)
    (1460, 1003),   # version 22 (105x105)
    (1588, 1091),   # version 23 (109x109)
    (1704, 1171),   # version 24 (113x113)
    (1853, 1273),   # version 25 (117x117)
    (1990, 1367),   # version 26 (121x121)
    (2132, 1465),   # version 27 (125x125)
    (2223, 1528),   # version 28 (129x129)
    (2369, 1628),   # version 29 (133x133)
    (2520, 1732),   # version 30 (137x137)
    (2677, 1840),   # version 31 (141x141)
    (2840, 1952),   # version 32 (145x145)
    (3009, 2068),   # version 33 (149x149)
    (3183, 2188),   # version 34 (153x153)
    (3351, 2303),   # version 35 (157x157)
    (3537, 2431),   # version 36 (161x161)
    (3729, 2563),   # version 37 (165x165)
    (3927, 2699),   # version 38 (169x169)
    (4087, 2809),   # version 39 (173x173)
    (4296, 2953),   # version 40 (177x177)
)


IMAGE_PREFIX = 'qr'


def encode_hex(data_file):
    hex_filename = tempfile.mkstemp()[1]
    with open(data_file, 'rb') as fin:
        with open(hex_filename, 'w') as fout:
            fout.write(b2a_hex(fin.read()).upper())
    return hex_filename


def qr_save(filepath, data, version=40):
    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data, optimize=0)
    qr.make(fit=True)

    img = qr.make_image()
    img.save(filepath)


def qr_large_file_save(data_file, split_size, output_dir, version=40):
    with open(data_file, 'rb') as f:
        index = 0
        data = f.read(split_size)
        while data:
            # generate
            image_path = '%s/%s_%06d.png' % (
                output_dir, IMAGE_PREFIX, index)
            qr_save(image_path, data, version)

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
    parser.add_argument('--qr-version', action='store', type=int, default=40,
                        help='specify QR code version. lower version is lower \
                        capacity, but QR image is being recognized easily. \
                        (1 - 40, default: 40)')
    parser.add_argument('--hex', action='store_true', default=False,
                        help='encode with hex (for most QR readers, which \
                        do not support to save the binary data.)')
    parser.add_argument('file', type=str, help='data file')
    args = parser.parse_args()
    output_dir = args.output_dir
    hex = args.hex
    qr_version = args.qr_version
    data_file = args.file

    # check QR version
    if qr_version < 1 or 40 < qr_version:
        print >> sys.stderr, 'QR version must be in a range: 1 - 40'
        sys.exit(1)

    # creates output directory if not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # maximum size using an binary character type
        split_size = QR_L_MAX_BYTES[qr_version - 1][1]

        # hex encode if option specified
        encoded_file = None
        if hex:
            encoded_file = encode_hex(data_file)
            data_file = encoded_file
            # QR Alphanumeric characters can include hex ones
            split_size = QR_L_MAX_BYTES[qr_version - 1][0]

        # generate QR images
        qr_large_file_save(data_file,
                           split_size,
                           output_dir,
                           version=qr_version)
    except:
        if encoded_file is not None and os.path.exists(encoded_file):
            os.remove(encoded_file)
        raise
        
    sys.exit(0)


if __name__ == "__main__":
    main()
