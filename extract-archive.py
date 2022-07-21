#!/usr/bin/python3

import argparse
import os
import tempfile
from io import SEEK_CUR

AR_FILE_NAME_SIZE = 16
AR_SIZE_OFFSET = 32
AR_SIZE_SIZE = 10
AR_FILE_START_OFFSET = 2


class CaseInsensitiveDict():
    def __init__(self):
        self._d = dict()

    def __contains__(self, k):
        return k.lower() in self._d

    def __len__(self):
        return len(self._d)

    def __iter__(self):
        return iter(self._d)

    def __getitem__(self, k):
        return self._d[k.lower()]

    def __setitem__(self, k, v):
        self._d[k.lower()] = v

    def get(self, k, default=None):
        if k.lower() in self._d:
            return self._d[k.lower()]
        else:
            return default


def is_file_system_case_sensitive():
    with tempfile.NamedTemporaryFile(prefix='TmP') as tmp_file:
        return(not os.path.exists(tmp_file.name.lower()))


def extract_archive(archive_path, destination_path):

    archive = open(archive_path, 'rb')

    global_header = archive.read(8)
    if global_header != str.encode('!<arch>\n'):
        print('Oops!, ' + archive_path + ' seems not to be an archive file!')
        exit(1)

    if is_file_system_case_sensitive():
        processed_files = dict()
    else:
        processed_files = CaseInsensitiveDict()

    count = 0
    while True:
        count = count+1
        ar_file_name_bytes = archive.read(AR_FILE_NAME_SIZE)
        if len(ar_file_name_bytes) == 0:
            break
        ar_file_name_raw = ar_file_name_bytes.rstrip(b' ').decode()
        archive.seek(AR_SIZE_OFFSET, SEEK_CUR)
        ar_file_size = int(archive.read(AR_SIZE_SIZE).rstrip(b' ').decode())
        if ar_file_name_raw.startswith('#1/'):
            file_name_size = int(ar_file_name_raw.replace('#1/', ''))
            ar_file_size = ar_file_size - file_name_size
            archive.seek(AR_FILE_START_OFFSET, SEEK_CUR)
            ar_file_name = archive.read(file_name_size).rstrip(b'\x00').decode()
        else:
            ar_file_name = ar_file_name_raw.decode()
            archive.seek(AR_FILE_START_OFFSET, SEEK_CUR)

        if ar_file_name in processed_files:
            filename, ext = os.path.splitext(ar_file_name)
            new_file_name = str(processed_files[ar_file_name] + 1) + '-' + filename + ext
            processed_files[ar_file_name] = processed_files[ar_file_name] + 1
        else:
            new_file_name = ar_file_name

        processed_files[ar_file_name] = processed_files.get(ar_file_name, 1)

        with open(os.path.join(destination_path, new_file_name), 'wb') as out:
            out.write(archive.read(ar_file_size))

        if archive.tell() % 2 == 1:
            archive.read(1)

    archive.close()


parser = argparse.ArgumentParser(description='Extract archive files.')
parser.add_argument('--archive', type=str, help='Path to the archive to extract')
parser.add_argument('--destination', type=str, help='Path to the destination')
args = parser.parse_args()

extract_archive(args.archive, args.destination)
