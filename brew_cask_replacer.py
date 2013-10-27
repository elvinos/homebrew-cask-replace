#!/usr/bin/env python
# coding=utf-8

import sys
import os
import commands
import urllib2
import json
from send2trash import send2trash

_CASKS_HOME = 'http://raw.github.com/phinze/homebrew-cask/master/Casks/'
_PROPERTY_NAMES = ['url', 'homepage', 'version', 'link']

def is_installed_by_appstore(application_path):
    output = commands.getoutput('codesign -dvvv "{0}"'.format(application_path))
    return output.find('Authority=Apple Mac OS Application Signing') > 0

def replace_application_in(applications_dir, always_yes = False, skip_app_from_appstore = True):
    installed_failed = []
    send2trash_failed = []
    applications = os.listdir(applications_dir)
    for application in applications:
        application_path = os.path.join(applications_dir, application)
        if skip_app_from_appstore and is_installed_by_appstore(application_path):
            continue
        application_name, ext = os.path.splitext(application)
        if ext.lower() != '.app':
            continue
        application_name = application_name.lower()
        application_name = '-'.join(application_name.split())
        try:
            application_info_file = urllib2.urlopen(_CASKS_HOME + application_name + '.rb')
        except Exception, e:
            continue
        application_info = {}
        for line in application_info_file:
            line = line.strip()
            key_value = line.split()
            if len(key_value) != 2:
                continue
            key = key_value[0]
            if key not in _PROPERTY_NAMES:
                continue
            application_info[key] = key_value[1]
        print('{0} -> {1}'.format(application, json.dumps(application_info,
            indent=4, separators=(',', ': '))))

        if not always_yes:
            replace_it = raw_input('Replace It(Y/n):')
            replace_it = replace_it.lower()
            if len(replace_it) > 0 and replace_it != 'y' and replace_it != 'yes':
                continue
        status = os.system('brew cask install {0}'.format(application_name))
        if status != 0:
            installed_failed.append(application)
            print('Install {0} fail'.format(application))
            continue
        try:
            send2trash(os.path.join(applications_dir, application))
        except Exception, e:
            send2trash_failed.append(os.path.join(applications_dir, application))
            print('Send {0} to trash fail with {1}'.format(application, e))
    print('Not replaced: {0}'.format([x for x in applications if x not in installed_failed]))
    print('Installed failed: {0}'.format(installed_failed))
    print('Send to trash failed: {0}'.format(send2trash_failed))

def main():
    applications_dir = '/Applications'
    always_yes = '-y' in sys.argv
    if always_yes:
        sys.argv.remove('-y')
    skip_app_from_appstore = True
    if '-f' in sys.argv:
        sys.argv.remove('-f')
        skip_app_from_appstore = False
    if len(sys.argv) > 1:
        applications_dir = sys.argv[1]
    replace_application_in(applications_dir, always_yes, skip_app_from_appstore)

if __name__ == '__main__':
    main()
