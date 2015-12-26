#!/usr/bin/env python

import argparse
import base64
import os
import os.path
import qrcode
import sys
import tempfile

from struct import *


# http://www.qrcode.com/en/about/version.html
QR_40_L_MAX_BINARY_BYTES = 2953

IMAGE_PREFIX = 'qr'


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
    parser = argparse.ArgumentParser(description='generate QR images.')
    parser.add_argument('--output-dir', dest='output_dir',
                        action='store', default='./out',
                        help='QR output directory (default: ./out)')
    parser.add_argument('file', type=str, help='data file')
    args = parser.parse_args()
    output_dir = args.output_dir
    data_file = args.file

    # creates output directory if not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # maximum size using an binary character type
        split_size = QR_40_L_MAX_BINARY_BYTES

        # generate QR images
        qr_large_file_save(data_file, split_size, output_dir)
    except:
        raise
        
    sys.exit(0)


if __name__ == "__main__":
    main()
