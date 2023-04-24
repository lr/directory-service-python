import ldap
import yaml

class DirectoryService:

    conn = None
    conf = None

    plainProto = 'ldap://'
    sslProto   = 'ldaps://'

    def __init__(self, conf_file_path = "conf/Config.yaml"):
        self.conf(conf_file_path)

    def conf(self, conf_file_path):
        """Loads the configuration from the conf_file_path."""

        f         = open(conf_file_path, 'r')
        self.conf = yaml.full_load(f)
        f.close()

    def connection(self, sourceString):
        """Gets the LDAP connection object given the provided sourceString name
           that is then used to look up the info from the config."""

        if (self.conn == None):
            source = self.conf['sources'][sourceString]
            ptoto  = self.plainProto
            if (source['useSSL']):
                proto = self.sslProto

            conn_string = proto + source['address'] + ':' + source['port']
            self.conn   = ldap.initialize(conn_string)
            self.conn.simple_bind_s(source['bindDN'], source['bindPassword'])
        
        return self.conn

    def find(self, ditItem, searchFilter):
        """Finds LDAP objects given the provided ditItem and searchFilter. If
           the provided ditItem is the singular version and if an object is
           found, then just the DirectoryServiceEntry is returned. If the
           ditItem is the plural version, then a list of
           DirectoryServiceEntry objects is returned."""

        values = self.valuesFromDitItem(ditItem)

        result = self.connection(
            values['source']).search_s(values['baseDN'],
            ldap.SCOPE_SUBTREE,
            searchFilter)
        
        entries = []
        
        for dn, entry in result:
            dse = DirectoryServiceEntry(dn, entry, ditItem)
            if (values['plural'] == False):
                return dse
            else:
                entries.append(dse)
        
        return entries

    def add(self, ditItem, dn, modlist):
        values = self.valuesFromDitItem(ditItem)

        return self.connection(
            values['source']).add_s(dn, modlist)

    def delete(self, ditItem, dn):
        values = self.valuesFromDitItem(ditItem)

        return self.connection(
            values['source']).delete_s(dn)

    def modify(self, entry):
        values = self.valuesFromDitItem(entry.ditItem)
        
        return self.connection(
            values['source']).modify_s(entry.dn, entry.modifications)

    def valuesFromDitItem(self, ditItem):
        """Returns a dictionary of values that correspond to the supplied
           ditItem.
           TODO: Convert the config to this type of dictionary with the
           ditItems as the keys to the dictionary. This way we don't have to
           do this work each time we do a query."""
        values = {'baseDN': '', 'plural': True, 'source': ''}

        for key, val in self.conf['dit'].items():
            if (val['singular'] == ditItem or val['plural'] == ditItem):
                values['source'] = val['source']
                values['baseDN'] = key

                if (val['singular'] == ditItem):
                    values['plural'] = False

                break

        return values

class DirectoryServiceEntry:
    """An object that represents the LDAP entry."""

    dn            = None
    entry         = None
    ditItem       = None

    modifications = None

    def __init__(self, dn, entry, ditItem):
        object.__setattr__(self, 'dn', dn)
        object.__setattr__(self, 'entry', entry)
        object.__setattr__(self, 'ditItem', ditItem)
        object.__setattr__(self, 'modifications', [])

    def ldif(self):
        """Returns an LDIF string of the entry."""
        attrs = self.entry.keys()
        
        ldifString = "dn: " + self.dn + "\n"

        for attr in attrs:
            if attr in self.entry.keys():
                for i in range(len(self.entry[attr])):
                    ldifString += attr + ": " + self.entry[attr][i].decode('UTF-8') + "\n"

        return ldifString

    def __getattr__(self, attr):
        """Checks to see if we want instance variables, and if so, returns them.
           Otherwise it returns the value of the provided attr. If the attr ends
           with 'Values' then it retuns the value as an array, whether it has
           more the one value or not."""
        if attr == 'dn':
            return getattr(self, 'dn')
        elif attr == 'entry':
            return getattr(self, 'entry')
        elif attr == 'ditItem':
            return getattr(self, 'ditItem')
        elif attr == 'modifications':
            return getattr(self, 'modifications')
        else:
            attrName = attr.replace('Values', '')
            if (self.entry[attrName] != None):
                if (attr.endswith('Values')):
                    return self.entry[attrName]
                else:
                    return self.entry[attrName][0].decode('UTF-8')
            else:
                return None

    def __setattr__(self, attr, value):
        """Sets the value for an attr and keeps track of all changes in the
           modifications tuple."""
        
        """From: https://www.python-ldap.org/en/python-ldap-3.4.3/reference/ldap.html
           Each element in the list modlist should be a tuple of the form
           (mod_op,mod_type,mod_vals), where mod_op indicates the operation
           (one of ldap.MOD_ADD, ldap.MOD_DELETE, or ldap.MOD_REPLACE),
           mod_type is a string indicating the attribute type name, and
           mod_vals is either a string value or a list of string values to
           add, delete or replace respectively.
           For the delete operation, mod_vals may be None indicating that all
           attributes are to be deleted."""
        
        tup = ()
        if value == None:
            tup = (ldap.MOD_DELETE, attr, None)
        else:
            val = value
            if isinstance(value, str):
                val = [bytes(value, 'utf-8')]
            tup = (ldap.MOD_REPLACE, attr, val)

        getattr(self, 'modifications').append(tup)
