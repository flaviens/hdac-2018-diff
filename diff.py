import os
import subprocess
import shutil
from pathlib import Path
from collections import defaultdict

#  subprocess.call(args, *, stdin=None, stdout=None, stderr=None, shell=False, cwd=None, timeout=None, **other_popen_kwargs)¶

diff_mode = '-Bwu'

# Return True if files are different according to our criteria
def do_diff(file1, file2, outfile=None):
    opts=diff_mode
    if outfile == None:
        opts += 'q'
    else:
        outfile=open(outfile,'w')
    rc = subprocess.call(['diff', opts, file1, file2], stdout=outfile)
    if rc == 0:
        # Diff says the files are the same
        return False
    if rc == 1:
        # Diff says the files are different
        return True
    raise Exception('something went wrong diffing')

if __name__ == "__main__":

    #
    # For each source file in the reference (bug-injected), find the corresponding original PULPissimo file for diff.
    #
    original_source_paths = []
    bug_injected_paths = []

    # Original sources.
    for extension in ("sv", "v", "vhd"):
        original_source_paths += [path for path in Path('ips').rglob('*.{}'.format(extension))]
        original_source_paths += [path for path in Path('rtl').rglob('*.{}'.format(extension))]
    # Bug injected files.

    for extension in ("sv", "v", "vhd"):
        bug_injected_paths += [path for path in Path('bug_injected').rglob('*.{}'.format(extension))]

    num_original_source_files = len(original_source_paths)
    num_bug_injected_files    = len(bug_injected_paths)

    print("Number of original files:     {}".format(num_original_source_files))
    print("Number of bug injected files: {}".format(num_bug_injected_files))

    #
    # Compute new, modified and deleted files
    #

    new_file_paths      = []
    modified_file_paths = []
    deleted_file_paths  = []

    # New and modified files
    for bug_injected_path in bug_injected_paths:
        candidate_original_path = Path(*bug_injected_path.parts[1:])
        if os.path.isfile(candidate_original_path):
            if do_diff(candidate_original_path, bug_injected_path):
                modified_file_paths.append((candidate_original_path, bug_injected_path))
        else:
            new_file_paths.append(bug_injected_path)

    # Deleted files
    for original_source_path in original_source_paths:
        candidate_bug_injected_path = Path(os.path.join("bug_injected", str(original_source_path)))
        if not os.path.isfile(candidate_bug_injected_path):
            deleted_file_paths.append(original_source_path)

    #
    # Write the new, modified and deleted files
    #

    NEW_FILE_SUMMARY_PATH = "generated/new.txt"
    MODIFIED_FILE_SUMMARY_PATH = "generated/modified.sh"
    DELETED_FILE_SUMMARY_PATH = "generated/deleted.txt"

    # New files
    with open(NEW_FILE_SUMMARY_PATH, "w") as f:
        f.write('\n'.join(map(str, new_file_paths)))

    # Deleted files
    with open(MODIFIED_FILE_SUMMARY_PATH, "w") as f:
        f.write('\n'.join(map(lambda x: "diff {} {} {}".format(diff_mode, x[0], x[1]), modified_file_paths)))

    # Deleted files
    with open(DELETED_FILE_SUMMARY_PATH, "w") as f:
        f.write('\n'.join(map(str, deleted_file_paths)))


# To re-create a partial arborescence
