import os, shutil, stat, sys
from abc import ABC, abstractmethod
from collections import deque
from typing import Tuple, List, Dict, Iterator, Optional


# TODO: Deal with
#  (2) cases where a special path is set just before marking file to copy (e.g., in _WriteModules) (extra path used for finding dependencies
#  (5) dummy file for created files (so they are not copied, by are moved on a re-locate operation)
#  (7) relative source (as part of dependency copying)


class FileCopierError(Exception):
    pass

class FileObject(ABC):
    def __init__(self):
        return

    @abstractmethod
    def __str__(self) -> str:
        return ""

    @abstractmethod
    def copy_to(self, dest_root:str):
        return

    def get_dependencies(self) -> List["FileObject"]:
        return []

    @staticmethod
    def remove_file(target_path: str):
        if os.path.exists(target_path):
            os.chmod(target_path, stat.S_IWRITE)
            os.remove(target_path)
            pass
        return

class RealFileObject(FileObject):
    """Represents a real file that should be copied into frozen application."""
    def __init__(self, source_path: str, target_rel_path: str,
                 copy_dependencies: bool = False,
                 include_mode: bool = False,
                 force_write_access: bool = False,
                 relative_source: bool = False):
        """
        :param source_path: Path to source file.
        :param target_rel_path: Relative path where file should be copied (relative to the dest_root specified at the time of copying).
        :param copy_dependencies: If True, also find and copy dynamic libraries linked by the file.
        :param include_mode: If True, copies over file mode information.
        :param force_write_access: If True, forces write access on copied file. (overrides include_mode)
        :param relative_source: If True, then (on Linux only), any dependencies of the file that are in a subdirectory of the directory containing this file, will be placed in the same position relative to this file.
        """
        super().__init__()
        self.source_path = source_path
        self.target_rel_path = target_rel_path
        self.copy_dependencies = copy_dependencies
        self.force_write_access = force_write_access
        self.include_mode = include_mode
        self.relative_source = relative_source
        return

    def __str__(self):
        return f"<File {self.source_path} -> {self.target_rel_path}>"

    def copy_to(self, dest_root:str):
        """
        Copy the file into the specified target location relative to dest_path
        """
        abs_dest_root = os.path.abspath(dest_root)
        abs_target_path = os.path.join(abs_dest_root, self.target_rel_path)
        #ensure target path exists
        os.makedirs(os.path.dirname(abs_target_path), exist_ok=True)
        self.remove_file(abs_target_path)
        shutil.copyfile(self.source_path, abs_target_path)
        shutil.copystat(self.source_path, abs_target_path)
        if self.include_mode:
            shutil.copymode(self.source_path, abs_target_path)
        if self.force_write_access:
            if not os.access(abs_target_path, os.W_OK):
                mode = os.stat(abs_target_path).st_mode
                os.chmod(abs_target_path, mode | stat.S_IWUSR)
        return

class VirtualFileObject(FileObject):
    """Represents a file that should be created in frozen application, with specified content."""
    def __init__(self, data: bytes, target_rel_path: str):
        super().__init__()
        self.data: bytes = data
        self.target_rel_path = target_rel_path
        return

    def __str__(self):
        return f"<VirtualFile {len(self.data)} bytes -> {self.target_rel_path}>"

    def copy_to(self, dest_root:str):
        """
        Copy the file into the specified target location relative to dest_path
        """
        abs_dest_root = os.path.abspath(dest_root)
        target_abs_path = os.path.join(abs_dest_root, self.target_rel_path)
        os.makedirs(os.path.dirname(target_abs_path), exist_ok=True)
        self.remove_file(target_abs_path)
        with open(target_abs_path, "wb") as f:
            f.write(self.data)
        return

class FileCopier:
    def __init__(self):
        """
        :param target_directory: The target directory that all files will be copied into.
        """
        # dictionaries of source / target paths that have been marked for copying
        self.all_files: Dict[Tuple[Optional[str], str], FileObject] = {}
        self.copied_file_paths: Dict[str, List[FileObject]] = {}
        self.target_file_paths: Dict[str, FileObject] = {}
        self.dependencies_check_queue = deque()
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
                          force_write_access: bool = False,
                          include_mode: bool = False,
                          relative_source: bool = False):
        """Mark that file at fromLocation should be copied to toLocation in the
        target directory.
        :param from_path: The full path to the source file.
        :param to_rel_path: The relative path in the target directory.
        """
        if os.path.basename(from_path).startswith("Python"): print(f'{from_path} -> {to_rel_path}'); raise Exception

        from_path = os.path.realpath(from_path)
        to_rel_path = os.path.normcase(os.path.normpath(to_rel_path))
        pathTuple = (from_path, to_rel_path)
        if pathTuple in self.all_files:
            #TODO, print warning, and simply update options on the FileObject, including
            # raise FileCopierError("Already marked source-to-target copy "
            #                       f'\n source: {from_path}'
            #                       f'\n target: {to_rel_path}')
            fobj = self.all_files[pathTuple]
            if copy_dependencies: self.dependencies_check_queue.append(fobj)
            return
        if to_rel_path in self.target_file_paths:
            raise FileCopierError("Attempting to copying second file to same "
                                  f"destination: {to_rel_path}")

        fobj = RealFileObject(source_path=from_path,
                              target_rel_path=to_rel_path,
                              copy_dependencies=copy_dependencies,
                              force_write_access=force_write_access,
                              include_mode=include_mode,
                              relative_source=relative_source)
        self.all_files[pathTuple] = fobj
        if from_path not in self.copied_file_paths:
            self.copied_file_paths[from_path] = []
        self.copied_file_paths[from_path].append(fobj)
        self.target_file_paths[to_rel_path] = fobj
        if copy_dependencies: self.dependencies_check_queue.append(fobj)
        return

    def mark_file_to_create(self, to_rel_path: str, data: bytes):
        """
        Record that a file should be created at a specified location with specified contents.
        """
        to_rel_path = os.path.normcase(os.path.normpath(to_rel_path))
        pathTuple = (None, to_rel_path)
        if pathTuple in self.all_files:
            # TODO, simply update options on the FileObject
            raise FileCopierError("Attempting to create second file a location "
                                  f'\n target: {to_rel_path}')
        if to_rel_path in self.target_file_paths:
            raise FileCopierError("Attempting to copying second file to same "
                                  f"destination: {to_rel_path}")

        fobj = VirtualFileObject(target_rel_path=to_rel_path,
                                 data = data)
        self.all_files[pathTuple] = fobj
        self.target_file_paths[to_rel_path] = fobj
        return

    def add_dependencies(self):
        """Go through files marked for copying, and determine and add any additional
        files that are dynamically linked."""
        print("Adding dependencies for:")
        while len(self.dependencies_check_queue) > 0:
            fobj = self.dependencies_check_queue.popleft()
            print(f'  {fobj}')
            pass
        return

    def copy_all_files(self, dest_root: str):
        """Copies all marked files into the target directory."""
        for fobj in self.all_files.values():
            fobj.copy_to(dest_root=dest_root)
            print(f'Copying: {fobj}')
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