[app]

# (str) Title of your application
title = 来宾信息提取工具

# (str) Package name
package.name = visitorinfo

# (str) Package domain (needed for android/ios packaging)
package.domain = com.visitorinfo.app

# (str) Source code where the main.py live
source.dir = .

# (str) The main script to run
source.main = mobile_main.py

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,txt,db

# (str) Application versioning (method 1)
version = 2.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,pillow==10.0.0,sqlite3,pyjnius,android,requests

# (str) Supported orientation (landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android SDK version to use
android.sdk = 33

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android app theme, default is ok for Kivy-based app
android.theme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
android.whitelist = 

# (str) Path to a custom whitelist file
android.whitelist_src = 

# (str) Path to a custom blacklist file
android.blacklist_src = 

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
android.add_jars = 

# (str) python-for-android branch to use, defaults to master
p4a.branch = master

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
android.ouya.category = APP

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
android.ouya.icon.filename = %(source.dir)s/data/icon.png

# (str) XML file to include as an intent filters in <activity> tag
android.manifest.intent_filters = 

# (str) launchMode to set for the main activity
android.manifest.launch_mode = standard

# (list) Android additional libraries to copy into libs/armeabi
android.add_libs_armeabi = 

# (list) Android additional libraries to copy into libs/armeabi-v7a
android.add_libs_armeabi_v7a = 

# (list) Android additional libraries to copy into libs/arm64-v8a
android.add_libs_arm64_v8a = 

# (list) Android additional libraries to copy into libs/x86
android.add_libs_x86 = 

# (list) Android additional libraries to copy into libs/mips
android.add_libs_mips = 

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1