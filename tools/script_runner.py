# Runs a specified script, and outputs a file with a list of the binaries that were loaded

# notes: exec("blineapp.py") works, but this doesn't, got to figure out what is changing...
# can read off the loaded libraries (on OSX) with "vmmap [pid]", can get the current pid with os.getpid()

import sys, os

def run_script(script_path, args=[]):
    """Run a setup script in a somewhat controlled environment.
    """
    original_args = sys.argv.copy()
    tmp_global = {'__file__': script_path}
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
            print(f'args: {sys.argv}')
            print(f'cur dir: {os.path.abspath(os.curdir)}')
            print(f'search path: {sys.path}')
            with open(script_path, 'rb') as f:
                script_contents = f.read()
            # print(sys.path)
            print("Running script")
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

def do_job():
    script_path = sys.argv[1]
    args = sys.argv[2:]
    # script_name = os.path.basename(script_path)
    # script_dir = os.path.dirname(script_path)
    # os.chdir(script_dir)
    # sys.path = [script_dir] + sys.path[1:]
    run_script(script_path=script_path, args=args)
    return

if __name__ == "__main__":
    do_job()