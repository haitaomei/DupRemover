import hashlib
import os
import pathlib
import shutil
import sys


# Print iterations progress
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()


def process_files(root_dir, func, **kwargs):
    for root, sub_dirs, files in os.walk(root_dir):
        for cur_file in files:
            abs_path = os.path.join(root, cur_file)
            func(abs_path, **kwargs)


def aggregate_count_and_size(file_path, **kwargs):
    container: list = kwargs['statistic_arr']
    container[0] += 1
    container[1] += os.path.getsize(file_path)


def group_with_checksum(file_path, **kwargs):
    groupings: dict = kwargs['grouping']
    hashing = kwargs['hash']
    running_info: list = kwargs['state']
    progress_update = kwargs['progress_update']
    md5checksum = hashing(file_path)
    if md5checksum not in groupings:
        groupings[md5checksum] = []
    groupings[hashing(file_path)].append(file_path)
    running_info[0] += os.path.getsize(file_path)
    progress_update(running_info[0], running_info[1])


def md5(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def generate_plan(file_groupings):
    pending = []
    for _, (checksum, files) in enumerate(file_groupings.items()):
        if len(files) > 1:
            print('Same files found [checksum = ', checksum, ']:\n\t', files)
            i = 0
            for file in files:
                i = i + 1
                if i == 1:
                    continue  # skip the first file
                relative_path = pathlib.Path(*pathlib.Path(file).parts[1:])
                path_to_move = os.path.join(move_to_dir, relative_path)
                print('\t Plan to move', file, 'into', path_to_move)
                pending.append([file, path_to_move])
    return pending


def move_duplicated_files(plans, progress_update):
    i = 0
    for item in plans:
        path_from = item[0]
        path_to_move = item[1]
        dir_for_new_file = pathlib.Path(*pathlib.Path(path_to_move).parts[:-1])
        if not os.path.exists(dir_for_new_file):
            os.makedirs(dir_for_new_file)
        shutil.move(path_from, path_to_move)
        i += 1
        progress_update(i, len(plans))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Please run this program with\n\tpython main.py F:\\YOUR_DIR_NAME F:\\DELETE_FILE_DIR')
        sys.exit()

    base_dir = sys.argv[1]
    move_to_dir = sys.argv[2]
    print('Searching dir:', sys.argv[1], '\nMove duplicated files to:', sys.argv[2])
    print('-------------------------------------------------------------')
    print('Statistic of directory:', base_dir)
    # file_map = list_files(base_dir)
    file_statistics = [0, 0]
    process_files(base_dir, aggregate_count_and_size, statistic_arr=file_statistics)
    print('\tTotal files: ', file_statistics[0], 'total size: ', file_statistics[1])
    grouped_files = {}
    process_files(base_dir,
                  group_with_checksum,
                  grouping=grouped_files,
                  hash=md5,
                  state=[0, file_statistics[1]],
                  progress_update=printProgressBar)

    print('-------------------------------------------------------------')
    print('Finished searching, duplicated file and moving plans:')
    print('-------------------------------------------------------------')
    plan = generate_plan(grouped_files)

    print('Please type Y to execute the file moving plan')
    user_input = input()
    if user_input == 'Y':
        move_duplicated_files(plan, printProgressBar)
