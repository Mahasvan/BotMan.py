import os
import re
from threading import Thread
from threading import BoundedSemaphore
from threading import Lock

from pylint import epylint as linter
import file_handling

files_to_lint = list(file_handling.find_files(".", file_extensions=["py"]))

score_regex = r"(?<=Your code has been rated at ).+(?=\s\(previous)"

try:
    print("Preparing...")
    linter.py_run(files_to_lint[0], return_std=True)
    # We just want to run one file, so we have the "(previous)" line, which the regex depends on
except:
    pass

threads = []
semaphore = BoundedSemaphore(os.cpu_count())
lock = Lock()

ratings_list = []

def lint_file(file_path):
    semaphore.acquire()
    print("Linting:", file_path)
    (pylint_stdout, pylint_stderr) = (linter.py_run(f"{file} --disable=all", return_std=True))
    output = (pylint_stdout.read())
    rating_line = [x for x in output.split("\n") if "Your code has been rated at" in x]
    if rating_line:
        rating_line = rating_line[0].strip()
    else:
        return
    extracted_rating = re.findall(score_regex, rating_line)
    if extracted_rating:
        lock.acquire()
        ratings_list.append(extracted_rating[0])
        lock.release()
    semaphore.release()


for file in files_to_lint:
    threads.append(Thread(target=lint_file, args=(file,)))

print(f"Starting with {os.cpu_count()} threads...")
for thread in threads:
    thread.start()

for thread in threads:
    try:
        thread.join()
    except RuntimeError:
        pass

ratings_list = [float(x.split("/")[0]) for x in ratings_list]
final_rating = round(sum(ratings_list) / len(ratings_list), 2)
print(f"\n\033[1;46mCode Rating: {final_rating}/10\033[0m")
