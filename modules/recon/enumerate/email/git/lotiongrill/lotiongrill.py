from recon.core.module import BaseModule
from git import Repo
import subprocess
import tempfile
import shutil
import json
import re
import os

class Module(BaseModule):

    meta = {
        'name':'LOTIONGRILL',
        'author':'gwaffles (https://twitter.com/gwaffles_)',
        'description':'Enumerate email addresses from all of a github users repositories.',
        'options':(
                ('username', None, True, 'the target github username.'),
            ),
        'comments':(
                ('Best used when the target doesn\'t have many repositories.'),
            ),
    }

    def module_run(self):
        username = self.options['username']
        repositories = self.get_user_repos(username)
        paths = []

        self.output('Cloning git repositories...')
        for git_url in repositories:
            clone_path = tempfile.mkdtemp()
            paths.append(clone_path)
            self.clone_user_repository(git_url, clone_path)

        # Extract it all
        self.output('Extracting emails...')
        for path in paths:
            emails = self.extract_emails_from_repo(path)
            for email in emails:
                # add emails to database
                self.output(email)

        for _path in paths:
            shutil.rmtree(_path)

    def get_user_repos(self, username):
        info = []
        # it only makes sense to use the api.
        res = self.request('https://api.github.com/users/%s/repos' % username)
        repos = json.loads(res.raw)
        if isinstance(repos, list):
            for repo in repos:
                info.append(repo['clone_url'])
        return info

    def clone_user_repository(self, git_url, clone_path):
        Repo.clone_from(git_url, clone_path)

    def extract_emails_from_repo(self, repo_path):
        proc = subprocess.Popen('git log --pretty=format:"%ae"'.split(),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                cwd=os.path.abspath(repo_path))
        emails = proc.communicate()[0].split('\n')
        return sorted(set([email.replace('"', '') for email in emails]))
