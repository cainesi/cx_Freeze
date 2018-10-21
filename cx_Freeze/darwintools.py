import os
import sys
import subprocess
from typing import List


def _getMachOLoadCommands(path) -> List[List[str]]:
    """Returns a list of load commands in the specified file, based on otool."""
    shellCommand = 'otool -l "{}"'.format(path)
    commands = []
    currentCommand = None

    # split the output into separate load commands
    for line in os.popen(shellCommand):
        line = line.strip()
        if line[:12] == "Load command":
            if currentCommand is not None:
                commands.append(currentCommand)
                pass
            currentCommand = []
        if currentCommand is not None:
            currentCommand.append(line)
            pass
        pass
    if currentCommand is not None:
        commands.append(currentCommand)

    return commands


def _parseLibrariesFromCommandList(commands: List[List[str]]) -> List[str]:
    """Extracts list of paths to dynamic libraries from the list of Mach-O load commands."""
    libraries = []
    for command in commands:
        if len(command) < 4: continue
        cmdLine = command[1]
        commandLinePieces = cmdLine.strip().split(" ")
        if commandLinePieces[0] != "cmd": continue
        if commandLinePieces[1] != "LC_LOAD_DYLIB": continue
        pathline = command[3]
        pathline = pathline.strip()
        if not pathline.startswith("name "): continue
        pathline = pathline[4:].strip()
        pathline = pathline.split("(offset")[0].strip()
        libraries.append(pathline)
        pass
    return libraries


def _parseRPathsFromCommandList(commands: List[List[str]], loaderPath: str) -> List[str]:
    """
    Extracts the rpaths from the list of Mach-O load commands.
    :param commands: a list of the Mach-O load commands (each command being a list of strings being the lines output by otool -l)
    :param loaderPath: the directory to be used for @loader_path (i.e., the directory where source file located).
    """
    rpathsRaw = []
    rpaths = []
    for command in commands:
        if len(command) < 4: continue
        cmdLine = command[1]
        commandLinePieces = cmdLine.strip().split(" ")
        if commandLinePieces[0] != "cmd": continue
        if commandLinePieces[1] != "LC_RPATH": continue
        pathline = command[3]
        pathline = pathline.strip()
        if not pathline.startswith("path "): continue
        pathline = pathline[4:].strip()
        pathline = pathline.split("(offset")[0].strip()
        rpathsRaw.append(pathline)
        pass

    for path in rpathsRaw:
        if len(path) == 0: continue
        path = path.replace("@loader_path", loaderPath)

        # we ignore any entries that rely on @executable_path, since we cannot know where the executable would be.
        if path[0] == "@": continue
        rpaths.append(path)
        pass

    return rpaths


def getReferencedLibraries(filePath: str) -> List[str]:
    """
    Return a list of libraries referenced by the given Mach-O object file.
    """
    commands = _getMachOLoadCommands(path=filePath)
    libraries = _parseLibrariesFromCommandList(commands=commands)
    return libraries


def getRPathsFromFile(filePath: str, loaderPath: str = None) -> List[str]:
    """Returns the @rpath(s) used by the file at specified filePath."""
    if loaderPath == "":  # so that a "." is put at the front of paths when an empty loaderPath given, and they stay relative
        loaderPath = "."
    if loaderPath is None:
        loaderPath = os.path.dirname(filePath)
    commands = _getMachOLoadCommands(path=filePath)
    rpaths = _parseRPathsFromCommandList(commands=commands, loaderPath=loaderPath)
    return rpaths


def getAlternativeRPathReplacements(path: str, rpaths: List[str]) -> List[str]:
    """Returns a list of all ways that path could be completed with the given rpaths."""
    if path.find("@rpath") != 0: return [path]
    completions = []
    for rp in rpaths:
        completions.append(path.replace("@rpath", rp))
        pass

    return completions


def replaceRPath(path: str, rpaths: List[str]) -> str:
    """Take a dependency path returned by otool, and replaces @rpath, if present, using a list or rpaths."""
    if path.find("@rpath") != 0: return path  # @rpath not present, do not need to do anything
    for rpath in rpaths:
        newName = path.replace("@rpath", rpath)
        if os.path.isfile(newName): return newName
        pass
    testPath = path.replace('@rpath', sys.prefix + '/lib')  # alternatively, try using python lib directory for @rpath
    if os.path.isfile(testPath): return testPath

    return path


def tryToMakePathAbsolute(path: str, rpaths: List[str], loaderPath: str) -> str:
    """Takes a path an attempts to make it absolute by filling in @loader_path or @rpath prefixes, if present."""
    if path.find("@loader_path") == 0:
        return path.replace("@loader_path", loaderPath)
    if path.find("@rpath") == 0:
        return replaceRPath(path=path, rpaths=rpaths)
    # do not deal with @executable_path, because we do not know where the executable would be.
    return path


def changeLoadReference(fileName: str, oldReference: str, newReference: str, VERBOSE: bool=True):
    if VERBOSE:
        print("Redirecting load reference for <{}> {} -> {}".format(fileName, oldReference, newReference))
    subprocess.call(('install_name_tool', '-change', oldReference, newReference, fileName))
    return


def isMachOFile(path: str) -> bool:
    """Determines whether the file is a Mach-O file."""
    p = subprocess.Popen(("file", path), stdout=subprocess.PIPE)
    if "Mach-O" in p.stdout.readline().decode(): return True
    return False


if __name__ == "__main__":
    fname = "/Users/caines/Program/Blackliner/build/BLine.app/Contents/MacOS/QtCore"
    commands = _getMachOLoadCommands(fname)
    libraries = _parseLibrariesFromCommandList(commands)
    #print(commands)
    print(libraries)
    print(_parseRPathsFromCommandList(commands, "***"))
    pass