# default values of buildtime flags
# loads constants from a compile-time-created module cx_buildtime_constants_source.py or, if that module is not present, uses default values.
# also contains code to allow the variables to be reloaded (since the compile-time module might change several times during a single
# interpreter session -- e.g., if the cx_builder creates several different distribution packages in a single interpreter session)

print("** Importing cx buildtime flags **")

# ** default values **
# variables only used in building (but put here as a convenient way of getting them into the build script)

KEY_FILENAME = None  # location of key file
USERNAME = None  # username that package was built for
PACKAGENAME = None  # file name for output package (on windows, is used in builder script, on OSX used in setup script


def updateVariables(module):
    """Load the buildtime variables from the specified module."""

    global KEY_FILENAME
    global USERNAME
    global PACKAGENAME

    try:
        KEY_FILENAME = module.KEY_FILENAME
        USERNAME = module.USERNAME
        PACKAGENAME = module.PACKAGENAME
        pass
    except AttributeError:
        pass
    return

# Load the vairables once on startup.
try:
    import cx_constants_buildtime_source
    updateVariables(cx_constants_buildtime_source)
    # print("Testing flag: {}".format(cx_buildtime_constants_source.TESTING_VERSION))
except ModuleNotFoundError:
    pass

def forceRefresh():
    """Reload the buildtime variables (refreshing them if the underlying cx_buildtime_constants_source.py file has changed since last load."""
    print("** Refreshing cx buildtime flags **")
    try:
        import cx_constants_buildtime_source
        import importlib
        importlib.reload(cx_constants_buildtime_source)
        updateVariables(cx_constants_buildtime_source)
        pass
    except ModuleNotFoundError:
        pass
    return
