import pathlib

import unittest

from directory_service.directory_service import DirectoryService

class TestDirectoryService(unittest.TestCase):

    def setUp(self):
        self.ds = DirectoryService()
        self.groups_base_dn = 'ou=groups,dc=someu,dc=edu'

    def test_valuesFromDitItem(self):
        values = self.ds.valuesFromDitItem('person')
        assert values['baseDN'] == 'ou=people,dc=someu,dc=edu'
        assert values['plural'] == False
        assert values['source'] == 'directory'

    def test_findPerson(self):
        person = self.ds.find('person', '(uid=3)')
        assert person.givenName    == 'Mabel'
        assert person.description  == 'This is the description for Rockland, Mabel.'
        assert person.doesNotExist == None
        assert len(person.objectClassValues) == 5

    def test_findPeople(self):
        people = self.ds.find('people', "(sn=r*)")
        assert len(people) == 20
        assert people[0].givenName == 'Mabel'

    def test_findGroup1(self):
        group = self.ds.find('group', '(cn=service desk)')
        assert group.cn                == 'service desk'
        assert group.dn                == 'cn=service desk,ou=groups,dc=someu,dc=edu'
        assert group.uniqueMember            == 'uid=3,ou=people,dc=someu,dc=edu'
        assert len(group.uniqueMemberValues) == 1

    def test_findGroup2(self):
        group = self.ds.find('group', '(cn=faculty)')
        assert group.cn                      == 'faculty'
        assert group.dn                      == 'cn=faculty,ou=groups,dc=someu,dc=edu'
        assert group.uniqueMember            == 'uid=6,ou=people,dc=someu,dc=edu'
        assert len(group.uniqueMemberValues) == 2

    def test_addAndDeleteGroup(self):
        dn = "cn=test group," + self.groups_base_dn

        entry = [
            ('objectClass', [b'top', b'groupOfUniqueNames']),
            ('cn', [b'test group']),
            ('description', [b'This is a test group.']),
        ]
        result = self.ds.add('group', dn, entry)
        
        group = self.ds.find('group', '(cn=test group)')
        assert group.cn == 'test group'

        self.ds.delete('group', dn)
        
        deletedGroup = self.ds.find('group', '(cn=test group)')
        assert len(deletedGroup) == 0

    def test_ldif(self):
        group = self.ds.find('group', '(cn=service desk)')
        assert group.ldif() == """dn: cn=service desk,ou=groups,dc=someu,dc=edu
objectClass: top
objectClass: groupOfUniqueNames
uniqueMember: uid=3,ou=people,dc=someu,dc=edu
cn: service desk
description: This is the Service Desk group
"""

    def test_modEntry(self):
        person = self.ds.find('person', '(uid=100)')
        
        person.givenName = 'First'
        person.sn        = 'Last'
        person.cn        = [b'First Last', b'Last, First', b'First A Last']
        
        modded = self.ds.modify(person)

        refetchedPerson = self.ds.find('person', '(uid=100)')
        assert refetchedPerson.givenName == 'First'
        assert refetchedPerson.sn        == 'Last'
        assert len(refetchedPerson.cnValues) == 3
        
        refetchedPerson.givenName = 'Jill'
        refetchedPerson.sn        = 'Peters'
        refetchedPerson.cn        = [b'Jill Peters', b'Peters, Jill']
        modded = self.ds.modify(refetchedPerson)

if __name__ == '__main__':
    unittest.main()
