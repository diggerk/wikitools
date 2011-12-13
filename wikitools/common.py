import os
import ConfigParser

from suds.client import Client


class WikiClient(object):
    def __init__(self, profile_name=None):
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.expanduser('~/.wikitools'))

        if profile_name:
            section_name = profile_name
        else:
            section_name = os.environ['WIKITOOLS_PROFILE'] if 'WIKITOOLS_PROFILE' in os.environ else 'default'

        self.wiki_url = config.get(section_name, 'uri')
        self._wiki_user = config.get(section_name, 'username')
        self._wiki_pass = config.get(section_name, 'password')
        self.space_name = config.get(section_name, 'space')

        self.client = Client(self.wiki_url)
        self.auth = self.client.service.login(self._wiki_user, self._wiki_pass)
        self.service = self.client.service
