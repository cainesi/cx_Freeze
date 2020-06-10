import zipfile
import os
import cx_Freeze
from cx_Freeze import setup, Executable
from constants import revision, version, upgrade_code
from cx_setup_util import getQtPluginIncludes
from cx_constants_buildtime import KEY_FILENAME, USERNAME

PACKAGENAME = "TEST"

print("**\n** Starting CX setup script (OSX) **\n**")
print("cx constants\n key_filename: {}\n username: {}".format(KEY_FILENAME, USERNAME))


#Script to be invokes with python [scriptname] bdist_mac to create mac app bundle

# Hack to fix problem where files has pre-1980 timestamps (otherwise zipfile would simply throw an exception)

include_files = [] #where to find license document file, and where to place it in the distribution.

#include_files.append(("../Blackliner/resources/qt.conf", ""))  # add a qt.conf file to package -- this is needed so that the application correctly loads the bundled versions of the Qt libraries (even if others are available on system)


# force the inclusion of certain plugins that cx-freeze cannot find on its own
requiredPlugins = [
    "styles/libqmacstyle.dylib",
    "sqldrivers/libqsqlite.dylib",
    "printsupport/libcocoaprintersupport.dylib"
]
include_files += getQtPluginIncludes(pluginList=requiredPlugins)

keyFiles = []

build_options = {"build_exe":"cx_build/",  # subdirectory to do build in
                 "build_base": "cx_build_dists"  # subdirectory to place .app and .dmg packages in
                 }

zip_include_packages = ["PyQt5"]  # Cause the PyQt5 to be included in the package in the old way (only specifically required files).  This makes the package *much* smaller.
extraPackages = ["PyQt5.sip"]  # force PyQt5.sip to be included.

build_exe_options = { "include_files": include_files,
                      "zip_include_packages": zip_include_packages,
                      "packages": extraPackages,
                      }


#msi_data = { "Shortcut": shortcut_table }
#bdist_msi_options = { "upgrade_code": upgrade_code, "data": msi_data}

bdist_mac_options = {
    "bundle_name": "BLine",
}

bdist_dmg_options = {
    "volume_label": PACKAGENAME,
    # "applications_shortcut": True  # seems to cause the packaging process to freeze?
}

#print version
#exe = Executable(script = "../Blackliner/blineapp.py")  # , icon=os.path.join("resources","app_icon_2_512.icns"))

exe = Executable(script = "test.py")


setup(  name = "BLine application",
        author = "Ian Caines",
        maintainer = "Ian Caines",
        maintainer_email = "ian.caines@gmail.com",
        #url = "",
        version = version,
        description = "BLine application version v" + str(version),
        options = {"build":build_options, "build_exe" : build_exe_options, "bdist_mac": bdist_mac_options,
                   "bdist_dmg": bdist_dmg_options},
        executables = [exe]
        )