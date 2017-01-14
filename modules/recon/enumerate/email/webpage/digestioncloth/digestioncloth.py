from recon.core.module import BaseModule
import re

class Module(BaseModule):

    meta = {
    'name':'DIGESTIONCLOTH',
    'author':'gwaffles (https://twitter.com/gwaffles_)',
    'description':'Attempt to recover email addresses from a single webpage instance.',
    'options':(
            ('webpage', None, True, 'Page with email addresses.'),
        ),
    }

    def module_run(self):
        webpage = self.options['webpage']
        request = self.request(webpage)
        addresses = re.findall(r'([\w\.\-]+@[\w.]+)', request.raw)

        if not addresses:
            self.errror('No addresses found on webpage.')
            return

        emails = self.filter_array(addresses)
        for email in emails:
            self.output(email)

    def filter_array(self, array):
        unique = {}
        for item in array:
            unique[item] = 1
        return unique.keys()
