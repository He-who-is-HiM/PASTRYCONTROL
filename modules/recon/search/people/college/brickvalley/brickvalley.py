from recon.core.module import BaseModule
from bs4 import BeautifulSoup
import re

class Module(BaseModule):

    meta = {
    'name':'BRICKVALLEY',
    'author':'gwaffles (https://twitter.com/gwaffles_)',
    'description':'Search for contact information via people who attend Cornell University.',
    'options':(
            ('name', None, True, 'The name of person to search for.'),
        ),

    }

    def module_run(self):

        # Name of the person who attends Cornell University.
        name     = self.options['name'].replace(' ', '+')
        _content = BeautifulSoup(self.request('https://www.cornell.edu/search/people.cfm?q=%s&tab=people' % name).raw)
        _html    = _content.find_all("table", {"class": "results cu-table"})#.getText().replace('\n\n', '\n').replace('\n\n', '\n')

        for i in _html:
            i = str(i)
            name  = re.findall(r'<a href="people\.cfm\?netid=.*">(.*?)</a>', i)
            email = re.findall(r'<a href="mailto\:.*?">(.*?)</a>', i)

            if name and email:

                for _name, _email in zip(name, email):
                    if _email != '':
                        output = '%s | %s' % (_name, _email)
                        self.output(output)
