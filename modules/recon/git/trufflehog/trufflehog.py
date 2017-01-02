from recon.core.module import BaseModule
from recon.core.framework import Colors
from pydoc import pager
from git import Repo
import datetime
import tempfile
import string
import shutil
import math

class Module(BaseModule):

    meta = {
    'name':'TRUFFLEHOG',
    'author':'gwaffles (https://twitter.com/gwaffles_)',
    'description':'Searches through git repositories for high entropy strings, digging deep into commit history.',
    'options':(
            ('repo', None, True,'Git repository url.'),
        ),
    }

    def module_run(self):
        repo = self.options['repo']
        repo_name = repo.split('/')[-1]
        self.output("Searching through: %s" % repo_name)
        self.find_strings(repo)

    def shannon_entropy(self, data, iterator):
        if not data:
            return 0
        entropy = 0
        for x in (ord(c) for c in iterator):
            p_x = float(data.count(chr(x)))/len(data)
            if p_x > 0:
                entropy += - p_x*math.log(p_x, 2)
        return entropy

    def get_strings_of_set(self, word, char_set, threshold=20):
        count = 0
        letters = ""
        strings = []
        for char in word:
            if char in char_set:
                letters += char
                count += 1
            else:
                if count > 20:
                    strings.append(letters)
                letters = ""
                count = 0
        if count > threshold:
            strings.append(letters)
        return strings

    def find_strings(self, git_url):
        HEX_CHARS = "1234567890abcdefABCDEF"
        BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        project_path = tempfile.mkdtemp()

        Repo.clone_from(git_url, project_path)

        repo = Repo(project_path)

        for remote_branch in repo.remotes.origin.fetch():
            branch_name = str(remote_branch).split('/')[1]
            try:
                repo.git.checkout(remote_branch, b=branch_name)
            except:
                pass

            prev_commit = None
            for curr_commit in repo.iter_commits():
                if not prev_commit:
                    pass
                else:
                    diff = prev_commit.diff(curr_commit, create_patch=True)
                    for blob in diff:
                        printableDiff = blob.diff
                        foundSomething = False
                        lines = blob.diff.split("\n")
                        for line in lines:
                            for word in line.split():
                                base64_strings = self.get_strings_of_set(word, BASE64_CHARS)
                                hex_strings = self.get_strings_of_set(word, HEX_CHARS)
                                for string in base64_strings:
                                    b64Entropy = self.shannon_entropy(string, BASE64_CHARS)
                                    if b64Entropy > 4.5:
                                        foundSomething = True
                                        printableDiff = printableDiff.replace(string, Colors.R + string + Colors.N)
                                for string in hex_strings:
                                    hexEntropy = self.shannon_entropy(string, HEX_CHARS)
                                    if hexEntropy > 3:
                                        foundSomething = True
                                        printableDiff = printableDiff.replace(string, Colors.R + string + Colors.N)
                        if foundSomething:
                            commit_time =  datetime.datetime.fromtimestamp(prev_commit.committed_date).strftime('%Y-%m-%d %H:%M:%S')
                            self.output("Date: " + commit_time)
                            self.output("Branch: " + branch_name)
                            self.output("Commit: " + prev_commit.message)
                            # Because it's easier this way.
                            # press "q" to view the next commit.
                            # press "ctrl+c" then press "q" to exit viewing all commits.
                            pager(printableDiff)
                prev_commit = curr_commit
        shutil.rmtree(project_path)
