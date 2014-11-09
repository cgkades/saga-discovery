import os



class RepoBuilder():
    #currenlty built for RHEL based systems
    '''This is the RepoBuilder class. It builds repos for Redhat based systems
    (RHEL/Fedora/CentOS)
    '''
    def __init__(self):
        self.repos = {} # Dictionary {'repofilename': [{'header': '[header],'name': 'long name', 'URL': 'url://location','enabled':0|1, 'gpgcheck': 0|1}]}
        self.load_repos()

    def load_repos(self):
        '''Load repos into a dictionary from the files in /etc/yum.repos.d'''
        #files should be in the name.repo format
        file_list = os.listdir('/etc/yum.repos.d/') #returns an array
        for repo_file in file_list:
            f = open("/etc/yum.repos.d/%s" %(repo_file))
            lines = f.read().split('\n')
            f.close()

            tmp_array_of_dictionary = self._lines_to_repo_dictionary(lines)
            if tmp_array_of_dictionary:
                self.repos[repo_file] = tmp_array_of_dictionary

    def _lines_to_repo_dictionary(self, lines):
        if len(lines) < 5:
            print "Error parsing repo file %s" % (repo_file,)
            return None

        if '[' not in lines[0] and ']' not in lines[0]:
            print "Repo file not formatted corectly"
            return None

        tmpd = {}
        item = 0
        for line in lines:
            if len(line) > 0 and '[' in line[0]:
                item = item + 1
                tmpd[item] = {}
                tmpd[item]['header'] = line
            elif len(line) > 0 and '#' not in line[0]:
                spl_line = line.split('=')
                if len(spl_line) > 1:
                    tmpd[item][spl_line[0]] = spl_line[1]
        return_array = []
        for key in tmpd:
            return_array.append(tmpd[key])
        return return_array

    def install_repo(self, repo_array):
        #check to make sure we don't already have the repo
        repos_to_add = []
        for item in repo_array:
            if not self._is_in_repo(item['name']):
                repos_to_add.append(item)

        if repos_to_add == []:
            return
        for repo in repos_to_add:
            self._create_repo_file(repo)
        self.load_repos()

    def _is_in_repo(self, repo_string):
        if self.repos == {}:
            return False
        repository = "[" + repo_string + "]"
        for key in self.repos:
            for repo in self.repos[key]:
                if repository in repo['header']:
                    return True

        return False

    def _create_repo_file(self, repo_dictionary):
        name = repo_dictionary['name']
        url = repo_dictionary['url']
        location = repo_dictionary['location']

        f = open("/etc/yum.repos.d/%s.repo" % (name,),'w')
        f.write("[%s]\n" % (name,))
        f.write("name=Repo in %s\n" % (location,))
        f.write("url=%s\n" % (url,))
        f.write("enabled=1\n")
        f.write("gpgcheck=0\n")
        f.close()
