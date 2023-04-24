# directory-service-python
Python3 version of the DirectoryService functionality. Limited functionality at this time, but enough to be (somewhat) useful.

# Usage
## Config
Us the provided example `conf/Config.yaml.template` file to map out your LDAP directory and its DIT. You can have more than one directory configured simply by creating multiple `sources` and then referencing the given source in the `dit` section. If you have two DNs that are the same, just change the case slightly (as keys have to be unique).

## Instantiate/Find/Add/Delete/Mod
For now, see the test cases for how to do these things. More details coming soon.

## Testing
In order to test this module, you will need a real LDAP server with live data (no mocks here). See the (directory-data)[https://github.com/lr/directory-data] project for details on setting up (OpenDJ)[https://github.com/OpenIdentityPlatform/OpenDJ] with data.

If you have all of that set up, then you can run the tests with:
    python -m unittest
