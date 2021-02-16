from typing import Tuple, List, Dict, Iterator, Optional
import os, shutil, stat, sys

#TODO - implement this in parallel to the existing _CopyFile code, and check that it produces the same result.

class FileCopierError(Exception):
    pass

class FileObject:
    def __init__(self, source_location: str, target_relative_location: str,
                 copy_dependencies: bool = False,
                 force_write_access: bool = False):
        self.source_path = source_location
        self.target_relative_path = target_relative_location
        self.copy_dependencies = copy_dependencies
        self.force_write_access = force_write_access
        return

    def __str__(self):
        return f"<File {self.source_path} -> {self.target_relative_path}>"

    def get_absolute_target_path(self, relative_to: str):
        """Returns the absolute target path of the file in the specified target
        directory"""
        relative_to = os.path.realpath(os.path.abspath(relative_to))
        return os.path.join(relative_to, self.target_relative_path)

class FileCopier:
    def __init__(self):
        """
        :param target_directory: The target directory that all files will be copied into.
        """
        # dictionaries of source / target paths that have been marked for copying
        self.all_files: Dict[Tuple[str, str], FileObject] = {}
        self.copied_file_paths: Dict[str, List[FileObject]] = {}
        self.target_file_paths: Dict[str, FileObject] = {}
        return

    def print_copy_report(self):
        source_paths = list(self.copied_file_paths.keys())
        source_paths.sort()
        print("Source files copied:")
        for p in source_paths:
            print(f'  {p}')
        return

    def get_full_target_path(self, relative_path: str) -> str:
        return os.path.realpath(os.path.join(self.target_directory, relative_path))

    def file_is_marked_to_copy(self, source_location: str) -> bool:
        """Returns True if the specified file is already marked for copying,
        else False."""
        if source_location in self.copied_file_paths: return True
        return False

    def file_objects_for_source_path(self, source_location: str) -> List[FileObject]:
        """Gets the FileObject for a file marked for copying."""
        if source_location not in self.copied_file_paths:
            raise FileCopierError("Attempt to get file object for file not" 
                                  f"marked for copying: {source_location}")
        return self.copied_file_paths[source_location]

    def mark_file_to_copy(self, from_path: str, to_rel_path: str,
                          copy_dependencies: bool = False,
                          force_write_access: bool = False):
        """Mark that file at fromLocation should be copied to toLocation in the
        target directory.
        :param from_path: The full path to the source file.
        :param to_rel_path: The relative path in the target directory.
        """
        #TODO: Deal with (1) relative source (figure out what it means!)
        #  (2) cases where a special path is set just before marking file to copy (e.g., in _WriteModules
        # (3) include_mode flag
        # (4) a copy action where there is no source file -- instead data is specified to be copied to a path
        # (5) dummy file for created files (so they are not copied, by are moved on a re-locate operation)

        # if os.path.basename(from_path).startswith("Python"): print(f'{from_path} -> {to_rel_path}'); raise Exception

        from_path = os.path.realpath(from_path)
        pathTuple = (from_path, to_rel_path)
        if pathTuple in self.all_files:
            #TODO, simply update options on the FileObject
            # raise FileCopierError("Already marked source-to-target copy "
            #                       f'\n source: {from_path}'
            #                       f'\n target: {to_rel_path}')
        # Allow a source file to be copied to multiple locations in freeze.
        # if from_location in self.copied_file_paths:
        #     raise FileCopierError("Attempting to re-mark file already marked "
        #                           f"for copying: {from_location}")
            return
        if to_rel_path in self.target_file_paths:
            raise FileCopierError("Attempting to copying second file to same "
                                  f"destination: {to_rel_path}")

        fobj = FileObject(source_location=from_path,
                          target_relative_location=to_rel_path,
                          copy_dependencies=copy_dependencies,
                          force_write_access=force_write_access)
        self.all_files[pathTuple] = fobj
        if from_path not in self.copied_file_paths:
            self.copied_file_paths[from_path] = []
        self.copied_file_paths[from_path].append(fobj)
        self.target_file_paths[to_rel_path] = fobj
        return

    def add_dependencies(self):
        """Go through files marked for copying, and determine and add any additional
        files that are dynamically linked."""
        # TODO: complete this
        return

    def copy_all_files(self, target_path: str):
        """Copies all marked files into the target directory."""

        # print(f"\n\n copy_all_files() to {target_path}")
        for fobj in self.all_files.values():
            dest_path = fobj.get_absolute_target_path(relative_to=target_path)
            # print(f"Trying to copy {fobj} to {dest_path}")

            # ensure destination directory exists
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            # print(f'Copying {fobj.source_path} -> {dest_path}')
            shutil.copyfile(fobj.source_path, dest_path)
            shutil.copystat(fobj.source_path, dest_path)
            if fobj.force_write_access:
                if not os.access(dest_path, os.W_OK):
                    mode = os.stat(dest_path).st_mode
                    os.chmod(dest_path, mode | stat.S_IWUSR)
            pass
        return

    def fixup_dynamic_links(self, path: str):
        """Where necessary, fixes dynamic links appearing in copied files.  Only required
        for Darwin.
        :param path: The location where all the files are located when doing the fixup
        (this is different from target_directory, since files will have been copied into
        app bundle directory)
        """
        # TODO: complete this
        if sys.platform != "darwin":
            return
        return