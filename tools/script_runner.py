
# Runs a specified script, and outputs a file with a list of the binaries that were loaded


import sys, os, subprocess
from typing import List, Set

VERBOSE = False
OUTPUT_WITH_NUMBERS = True
DARWIN_USE_VMMAP = False  # vmmap is not ideal, since it seems to hide full paths to libraries in user folder

tmp_global = {}

def run_script(script_path, args=[]):
    """
    Run a script from a specified file in a somewhat controlled environment.
    :param script_path: Path to script to be run.
    :param args: Arguments to provide to script.
    """
    original_args = sys.argv.copy()
    global tmp_global
    tmp_global = {'__file__': script_path,
                  '__name__': '__main__'}
    script_path = os.path.abspath(script_path)
    script_dir = os.path.dirname(script_path)
    original_search_path = sys.path
    sys.path = [script_dir] + sys.path[1:]
    original_directory = os.path.abspath(os.curdir)
    os.chdir(script_dir)
    sys.argv[0] = script_path
    sys.argv[1:] = args
    try:
        try:
            print(f'running script: {script_path}')
            if VERBOSE:
                print(f'args: {sys.argv}')
                print(f'cur dir: {os.path.abspath(os.curdir)}')
                print(f'search path: {sys.path}')
            with open(script_path, 'rb') as f:
                script_contents = f.read()
            exec(script_contents, tmp_global)
            print("Script completed")
        finally: pass
    except SystemExit:
        print("WARNGING: Underlying script exited with error.")
        pass

    sys.path = original_search_path
    os.chdir(original_directory)
    sys.argv = original_args
    return

def loaded_module_list() -> List[str]:
    """Return a list of loaded modules."""
    return [k for k in sys.modules.keys()]

def loaded_libraries() -> List[str]:
    if sys.platform == "darwin":
        return loaded_libraries_darwin()
    elif sys.platform == "win32":
        return loaded_libraries_win()


    return []

def loaded_libraries_darwin() -> List[str]:
    lib_list: List[str] = []
    if DARWIN_USE_VMMAP: lib_list = loaded_libraries_darwin_vmmap()
    else: lib_list =  loaded_libraries_darwin_lsof()
    IGNORE_DIRECTORIES = ["/usr/lib/", "/System/Library/Frameworks/", "/System/Library/PrivateFrameworks/"]
    for excluded in IGNORE_DIRECTORIES:
        lib_list = [c for c in lib_list if not c.startswith(excluded)]
    # TODO: filter the list to only include dynamic libraries, to exclude other (e.g., data) files that happen to be open or memory-mapped.  See darwintools.py for example code. Problem at the moment is that vmmap can return obfuscated paths so we might not have the correct file path to test.

    return lib_list

def loaded_libraries_darwin_lsof() -> List[str]:
    pid = os.getpid()
    lcommand = ["/usr/sbin/lsof", "-p", str(pid)]
    result = subprocess.run(lcommand, capture_output=True, text=True)
    output = result.stdout
    outputLines = output.splitlines()
    if len(outputLines) == 0: return []
    firstLine = outputLines[0]
    filename_start_position = firstLine.find('NAME')
    open_files: Set[str] = set()

    if filename_start_position <= 0: return []
    for line in outputLines[1:]:
        path = line[filename_start_position:]
        if path.startswith("/"): open_files.add(path)
    return list(open_files)

def loaded_libraries_darwin_vmmap() -> List[str]:
    if VERBOSE: print("Checking binaries")
    pid = os.getpid()
    command = ["/usr/bin/vmmap", "-w", str(pid)]
    if VERBOSE: print(f'Check binaries command: {command}')
    result: subprocess.CompletedProcess= subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Error checking loaded libraries")
    output: str = result.stdout
    # print(f"Output: [{output}]")
    outputLines = output.splitlines()

    NONWRITABLE_REGIONS_START = "==== Non-writable regions for process"
    WRITEABLE_REGIONS_START = "==== Writable regions for process"
    FILENAME_COLUMN_HEADING = "REGION DETAIL"
    listing_regions = False
    title_line_next = False
    filename_start_position = 0

    mapped_files: Set[str] = set()

    for line in outputLines:
        if line.startswith("===="):
            listing_regions = False
            if line.startswith(NONWRITABLE_REGIONS_START) or line.startswith(WRITEABLE_REGIONS_START): title_line_next = True
            continue
        if title_line_next:
            title_line_next = False
            n = line.find(FILENAME_COLUMN_HEADING)
            if n > 0:
                listing_regions = True
                filename_start_position = n
            continue
        if listing_regions:
            path = line[filename_start_position:]
            if path.startswith("/"): mapped_files.add(path)

    return list(mapped_files)

def loaded_libraries_win() -> List[str]:
    raise Exception("loaded_libraries_win() not yet implemented")
    # should be able to use ListDLLs (from Windows sysinternals) to list the loaded dlls
    return []

def main():
    if len(sys.argv) < 2:
        print("Usage:\npython script_runner.py [path of script to test] [script arguments]")
        return
    script_path = sys.argv[1]
    args = sys.argv[2:]
    pre_run_modules = loaded_module_list()
    pre_run_libraries = loaded_libraries()
    run_script(script_path=script_path, args=args)
    post_run_modules = loaded_module_list()
    post_run_libraries = loaded_libraries()
    additional_modules = [c for c in post_run_modules if c not in pre_run_modules]
    additional_libraries = [c for c in post_run_libraries if c not in pre_run_libraries]

    additional_modules.sort()
    additional_libraries.sort()
    n = 1
    print(f'\nAdditional modules loaded by script: {script_path}')
    for m in additional_modules:
        print('    {}{}'.format(f'[{n: 3d}] ' if OUTPUT_WITH_NUMBERS else '', m))
        n += 1

    n = 1
    print(f'\nAdditional libraries loaded by script: {script_path}')
    for fname in additional_libraries:
        print('    {}{}'.format(f'[{n: 3d}] ' if OUTPUT_WITH_NUMBERS else '', fname))
        n += 1
    return

if __name__ == "__main__":
    main()