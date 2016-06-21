# PyggyBank

Symple Python password vault

## Usage
```
python passwords.py [option] password_key filename
```

Where:
* option can be `type` or `add` or `list`
* password_key is the key of the password (just to identify that password)
* filename is the name of the ENCRYPTED GPG file (leave empty for first time use)

### Options explained

#### type
Type the password after 10 seconds

#### add
Add a new password

#### list
List the all the password keys in the vault

The script will prompt for the .gpg password.
If `add`, this script will prompt for the new password as well.
