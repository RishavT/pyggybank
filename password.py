# !/usr/bin/python
"""
Simple script to read passwords from or add passwords to a .gpg file

Usage:
======
./passwords.py <option> password_key filename
Where:
* option can be `type` or `add` or `list`
* password_key is the key of the password (just to identify that password)
* filename is the name of the ENCRYPTED GPG file (leave empty for first time use)

The script will prompt for the .gpg password.
If `add`, this script will prompt for the new password as well.
"""

import time
import json
import subprocess
import os
import sys
import getpass

class PasswordManager(object):
    """Class to manage passwords"""

    def create_gpg_file(self):
        """Creates a .json file and encrypts it"""
        os.system('touch passwords.json.gpg')
        self.gpg_file = 'passwords.json.gpg'
        return

    def __init__(self, master_password, gpg_file=None):
        self.master_password = master_password
        self.passwords = {}
        if gpg_file:
            self.gpg_file = gpg_file
        else:
            self.create_gpg_file()

    def type(self, text):
        """Types a piece of text"""
        sp = subprocess.Popen(
            'osascript',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE)
        out, err = sp.communicate(
            input="tell application \"System Events\" to keystroke \"{0}\""
            .format(text))
        if err:
            print "Failed to type password."
            return
        return True

    def load_passwords(self):
        """Loads the passwords from the gpg file"""
        sp = subprocess.Popen(
            ['gpg', '--passphrase', self.master_password, self.gpg_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = sp.communicate()
        # TODO(rthakker) check error code also
        if 'bad key' in out or 'bad key' in err:
            print "Invalid password."
            return
        if not os.path.isfile('passwords.json'):
            print "Failed to load passwords."
            return
        self.passwords = json.loads(open('passwords.json').read())
        os.system('rm passwords.json')
        return True

    def save_passwords(self):
        """Saves the password and encrypts it"""
        os.system('mv {0} {0}.old'.format(self.gpg_file))
        with open('passwords.json', 'w') as outfile:
            outfile.write(json.dumps(self.passwords))
        sp = subprocess.Popen(
            ['gpg', '--passphrase', self.master_password, '-c', 'passwords.json'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = sp.communicate()
        os.system('rm passwords.json')
        if not os.path.isfile('passwords.json.gpg'):
            print 'Failed to save password'
            return
        os.system('mv passwords.json.gpg {0}'.format(self.gpg_file))
        return True

    def type_password(self, key, timeout):
        """Types a password after `timeout` seconds"""
        password = self.passwords.get(key)
        if not password:
            print "Invalid password key"
            return
        time.sleep(timeout)
        self.type(password)

    def get_password_keys(self):
        """Returns password keys"""
        if self.passwords:
            return self.passwords.keys()

    def add_password(self, key):
        """Adds a password"""
        if not key:
            return
        password = getpass.getpass('Enter Password')
        if password != getpass.getpass('Re-enter Password'):
            print "Passwords do not match!"
            return
        self.passwords[key] = password
        self.save_passwords()


def main():
    """Main function"""
    option = sys.argv[1]
    key = filename = None
    if len(sys.argv) >= 3:
        key = sys.argv[2]
    if len(sys.argv) >= 4:
        filename = sys.argv[3]

    # Read password from terminal
    password = getpass.getpass('Enter Master Password')

    # Re read password if required
    if not filename:
        if password != getpass.getpass('Re-enter Master Password'):
            print "Passwords don't match"
            return
    pwd_manager = PasswordManager(master_password=password, gpg_file=filename)
    pwd_manager.load_passwords()

    if option == 'type':
        print "Typing password in 10 seconds.."
        pwd_manager.type_password(key, 10)
    elif option == 'list':
        print pwd_manager.get_password_keys()
    elif option == 'add':
        pwd_manager.add_password(key)

if __name__ == "__main__":
    main()
