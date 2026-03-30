import argparse
import os

from os import listdir
from os.path import isfile, join


def get_files(target_path):
    return [f for f in listdir(target_path) if isfile(join(target_path, f))]


def rename(target_path, file_names):
    print(f"Scan {len(files)} files")
    for target_file in file_names:
        parts = target_file.split("-")
        if len(parts) != 3:
            continue

        source_file = os.path.join(target_path, target_file)
        target_file = os.path.join(target_path, parts[2])
        os.rename(source_file, target_file)
        print(source_file, "-->", target_file)


def print_statistics(target_path):
    global files
    files = get_files(target_path)
    numbers = set()
    for file_name in files:
        parts = file_name.split('.jpg')
        if len(parts) == 2:
            numbers.add(int(parts[0]))
    missing = list()
    for i in range(1, max(numbers)):
        if i in numbers:
            continue
        missing.append(i)
    print(f"Found {len(missing)} files are not in the consecutive sequence")
    missing.sort()
    if len(missing) == 0:
        return
    start = missing[0]
    end = missing[0]
    missing_intervals = list()
    for i in missing:
        if i == start:
            continue
        else:
            if i > end + 1:
                missing_intervals.append((start, end))
                start = end = i
            else:
                end = i
    missing_intervals.append((start, end))
    if len(missing_intervals) == 0:
        return
    debug_info = []
    for start, end in missing_intervals:
        debug_info.append(f"{start} - {end}.jpg")
    summary = ", ".join(debug_info)
    print(f"The follow files might be missing:\n{summary}")
    print("")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Bulk file rename',
        description='Bulk rename files in a directory',
        epilog='')
    parser.add_argument('-p', '--path')
    args = parser.parse_args()
    path = args.path
    if path is None:
        parser.print_help()
    else:
        files = get_files(path)
        rename(path, files)

    print_statistics(path)
