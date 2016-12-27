from recon.core.module import BaseModule
import json

class Module(BaseModule):

    meta = {
    'name':'DIPLOMAPACKAGE',
    'author':'gwaffles (https://twitter.com/gwaffles_)',
    'description':'Search for contact information via people who attend Virginia Polytechnic Institute.',
    'options':(
            ('name', None, True, 'The name of person to search for.'),
        ),
    'comments':(
            ('The name of the person you are looking for can be the first and or last name.'),
        )
    }

    def module_run(self):
        # Parsed name query.
        query  = self.parse_query(self.options['name'])

        # Original query without being parsed for displaying purposes.
        oquery = self.options['name']

        # Json GET request to piggyback off of.
        resource = 'https://webapps.middleware.vt.edu/peoplesearch/JsonSearch?query=%s' % query

        # The amount of peoples information that has been found from our query, if any.
        information = json.loads(self.request(str(resource)).raw)

        # The amount of people the query returns, if any at all.
        amount = len(information)

        if amount == 0:
            self.error('Name not found.')

        elif amount > 1:
            self.output('Found %d people with the name %s.' % (amount, oquery))

        elif amount == 1:
            self.output('Found 1 person with the name %s.' % oquery)

        for info in information:
            # Since we search the database with a 'name' query,
            # a name is always a guaranteed factor that the results will always return.

            if info.has_key('cn') is True and info.has_key('mail') is True and info.has_key('localPhone') is True:
                # For scenarios when a person has a name, email address and contact phone number.
                person_name  = info['cn'][0]
                person_email = info['mail'][0]
                person_phone = info['localPhone'][0]
                output = '%s | %s | %s' % (person_name, person_email, person_phone)
                self.output(output)

            elif info.has_key('cn') is True and info.has_key('mail') is True and info.has_key('localPhone') is False:
                # For scenarios when a person doesn't have a contact phone number.
                person_name  = info['cn'][0]
                person_email = info['mail'][0]
                output = '%s | %s' % (person_name, person_email)
                self.output(output)

            elif info.has_key('cn') is True and info.has_key('mail') is False and info.has_key('localPhone') is True:
                # For scenarios when a person has a name, email address and contact phone number.
                person_name  = info['cn'][0]
                person_phone = info['localPhone'][0]
                output = '%s | %s' % (person_name, person_phone)
                self.output(output)

    def parse_query(self, query):
        query = query.replace(' ', '%20')
        return query

    def parse_phone_number(self, phone_number):
        # to be implemented
        pass
