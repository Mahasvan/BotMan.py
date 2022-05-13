import os


def count_lines(start=".", lines=0, blacklisted_dirs=["venv"], file_extensions=["py"]):
    for file in os.listdir(start):
        relative_path = os.path.join(start, file)
        if os.path.isfile(relative_path) and relative_path.split(".")[-1] in file_extensions:
            with open(relative_path, 'r', encoding='utf-8') as f:
                lines += len(f.readlines())
        elif os.path.isdir(relative_path) and file not in blacklisted_dirs:
            lines = count_lines(relative_path, lines, blacklisted_dirs, file_extensions)
    return lines


def find_files(start=".", files = [], blacklisted_dirs=["venv"], file_extensions=["py"]):
    for file in os.listdir(start):
        relative_path = os.path.join(start, file)
        if os.path.isfile(relative_path) and relative_path.split(".")[-1] in file_extensions:
            yield relative_path
        elif os.path.isdir(relative_path) and file not in blacklisted_dirs:
            yield from find_files(relative_path, blacklisted_dirs, file_extensions)
