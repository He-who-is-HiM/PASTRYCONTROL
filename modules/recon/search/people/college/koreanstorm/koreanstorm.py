from recon.core.module import BaseModule
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser

class Module(BaseModule):

    meta = {
    'name':'KOREANSTORM',
    'author':'gwaffles (https://twitter.com/gwaffles_)',
    'description':'Search for contact information via people who attend University of Minnesota.',
    'options':(
            ('name',None,True,'The name of person to search for.'),
            ('campus','a',True,'The campus the person is on.'),
            ('role','any',True,'The role the person plays on campus.'),
        ),

    'comments':(
        'Campus types:',
        '\t a = Any campus (default)',
        '\t c = Crookston',
        '\t d = Duluth',
        '\t m = Morris',
        '\t r = Rochester',
        '\t t = Twin Cities',
        '\t o = Other',
        'Role types:',
        '\t any = Any role (default)',
        '\t sta = Faculty/Staff',
        '\t stu = Student',
        '\t alu = Alumni',
        '\t ret = Retired Faculty',
        ),
    }

    def module_run(self):

        # Name of the person who attends the Universities events.
        name   = self.options['name'].replace(' ', '+')

        # The campus that hte person may attend events on.
        campus = self.options['campus']

        # The role the person plays on campus.
        role   = self.options['role']

        # Campuses
        cmus = [
        'a', #'Any campus'
        'c', #'Crookston'
        'd', #'Duluth'
        'm', #'Morris'
        'r', #'Rochester',
        't', #'Twin Cities',
        'o'  #'Other'
        ]

        # Roles
        rls = [
        'any', #'Any role',
        'sta', #'Faculty/Staff',
        'stu', #'Student',
        'alu', #'Alumni',
        'ret', #'Retired Faculty'
        ]

        if campus not in cmus:
            self.error('That campus doesn\'t exist.')

        elif role not in rls:
            self.error('That role doesn\'t exist.')

        _request = self.request('http://myaccount.umn.edu/lookup?SET_INSTITUTION=UMNTC&type=name&CN=%s&campus=%s&role=%s' % (name,campus,role))
        _content = BeautifulSoup(_request.raw)

        # Multiple instance results
        if self.is_multiple_results(_content):
            _mutltiple = self.parse_multiple_results(_content)

            for info in _mutltiple:
                if info.has_key('name') is True and info.has_key('email') is True and info.has_key('phone') is True:
                    # For scenarios when a person has a name, email address and contact phone number.
                    person_name  = info['name']
                    person_email = info['email']
                    person_phone = info['phone']
                    person_dept  = info['dept_or_college']
                    output = '%s | %s | %s | %s' % (person_name, person_email, person_phone, person_dept)
                    self.output(output)

                elif info.has_key('name') is True and info.has_key('email') is True and info.has_key('phone') is False:
                    # For scenarios when a person doesn't have a contact phone number.
                    person_name  = info['name']
                    person_email = info['email']
                    try:
                        person_dept  = info['dept_or_college']
                        output = '%s | %s | %s' % (person_name, person_email, person_dept)
                    except KeyError:
                            output = '%s | %s ' % (person_name, person_email)
                    self.output(output)

                elif info.has_key('name') is True and info.has_key('email') is False and info.has_key('phone') is True:
                    # For scenarios when a person has a name, email address and contact phone number.
                    person_name  = info['name']
                    person_phone = info['phone']
                    person_dept  = info['dept_or_college']
                    try:
                        person_dept  = info['dept_or_college']
                        output = '%s | %s | %s' % (person_name, person_email, person_dept)
                    except KeyError:
                            output = '%s | %s ' % (person_name, person_email)
                    self.output(output)

        # Single instance result
        elif self.is_single_result(_content):
            _single = self.parse_single_result(_content)

            for info in _single:
                if info.has_key('name') is True and info.has_key('email') is True and info.has_key('phone') is True:
                    # For scenarios when a person has a name, email address and contact phone number.
                    person_name  = info['name']
                    person_email = info['email']
                    person_phone = info['phone']
                    person_dept  = info['dept_or_college']
                    try:
                        person_dept  = info['dept_or_college']
                        output = '%s | %s | %s | %s' % (person_name, person_email, person_phone, person_dept)
                    except KeyError:
                        output = '%s | %s | %s' % (person_name, person_email, person_phone)
                    self.output(output)

                elif info.has_key('name') is True and info.has_key('email') is True and info.has_key('phone') is False:
                    # For scenarios when a person doesn't have a contact phone number.
                    person_name  = info['name']
                    person_email = info['email']
                    try:
                        person_dept  = info['dept_or_college']
                        output = '%s | %s | %s' % (person_name, person_email, person_dept)
                    except KeyError:
                        output = '%s | %s ' % (person_name, person_email)
                    self.output(output)

                elif info.has_key('name') is True and info.has_key('email') is False and info.has_key('phone') is True:
                    # For scenarios when a person has a name, email address and contact phone number.
                    person_name  = info['name']
                    person_phone = info['phone']
                    try:
                        person_dept  = info['dept_or_college']
                        output = '%s | %s | %s' % (person_name, person_email, person_dept)
                    except KeyError:
                        output = '%s | %s ' % (person_name, person_phone)
                    self.output(output)

        elif self.is_no_results(_content):
            self.error('No results were found for %s.' % name.replace('+', ' '))

        elif self.is_too_many_results(_content):
            self.error('Too many results were found for %s.' % name.replace('+', ' '))

    def strip_tags(self, html):
        HTMLParser.feed(html)
        return HTMLParser.get_data()

    def replace_br_with_newline(self, html):
        return html.replace('<br>', '\n').replace('</br>', '\n')

    def parse_multiple_results(self, soup):
        fields = ['name', 'email', 'work_phone', 'phone', 'dept_or_college']
        rows = soup.find(id='pagecontent').find('table').find_all('tr')
        all_rows = []
        for row in rows:
            cells = row.find_all('td')
            row_data = {}
            for cell_num in xrange(len(cells)):
                cell_data = cells[cell_num]
                cell_text = cell_data.text
                cell_field = fields[cell_num]
                if cell_text.strip() != '':
                    row_data[cell_field] = cell_text.replace(u'\xa0', u' ')
                if cell_num == 0:
                    url = cell_data.find('a')['href']
                    row_data['url'] = url
                    x500 = url.split('&UID=')[1]
                    row_data['x500'] = x500
            all_rows.append(row_data)
        all_rows.pop(0)
        return all_rows

    def parse_single_result(self, soup):
        data = soup.find(id='pagecontent').find('table').find_all('tr')
        parsed = {}
        for kv_pair in data:
            key = kv_pair.find('th').text.strip().lower().replace(' ', '_')
            value_html = str(kv_pair.find('td'))
            value = self.strip_tags(self.replace_br_with_newline(value_html)).strip()
            parsed[key] = value
        return parsed

    def is_multiple_results(self, soup):
        try:
            table_present = soup.find(id='pagecontent').find('table')
            h2_present = soup.find(id='pagecontent').find('h2')
            return (table_present and not(h2_present)) == True
        except AttributeError: # catch None.find()
            return False

    def is_single_result(self, soup):
        try:
            result = soup.find(id='pagecontent').find('h2')
            return result != None
        except AttributeError: # catch None.find()
            return False

    def is_no_results(self, soup):
        # If no results are found.
        try:
            results = soup.find(id='pagecontent').find_all('b')
            for result in results:
                if result.text == 'No matches found.':
                    return True
            return False
        except AttributeError: # catch None.find()
            return False

    def is_too_many_results(self, soup):
        # If the search criteria was too general.
        try:
            results = soup.find(id='pagecontent').find_all('b')
            for result in results:
                if result.text == 'Too many entries matched your search criteria. Please try again with more specific criteria. ':
                    return True
            return False
        except AttributeError: # catch None.find()
            return False
