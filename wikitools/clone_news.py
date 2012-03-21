import sys
import logging
from datetime import datetime

from wikitools.common import WikiClient


logger = logging.getLogger(__name__)


class CloneNews(object):
    def __init__(self, from_profile, to_profile):
        self.src_client = WikiClient(from_profile)
        self.trg_client = WikiClient(to_profile)

    def clone_news(self, since_date=None):
        src_entries = self._get_entries(self.src_client, since_date)
        trg_entries = self._get_entries(self.trg_client, since_date)
        logger.info("Cloning %s blog entries", len(src_entries))
        for e in src_entries:
            trg = self._find_entry(trg_entries, e.publishDate, e.title)
            verb = 'Cloning' if not trg else 'Updating'
            logger.info("%s entry %s posted on %s", verb, e.title, e.publishDate)
            self.clone_entry(e.id, trg.id if trg else None)

    def clone_entry(self, entry_id, trg_entry_id):
        src_entry = self.src_client.service.getBlogEntry(self.src_client.auth, entry_id)
        trg_entry = self._create_entry(src_entry, trg_entry_id)
        if trg_entry:
            self.trg_client.service.storeBlogEntry(self.trg_client.auth, trg_entry)

    def _find_entry(self, entries, date, title):
        for e in entries:
            if e.publishDate.date() == date.date() and e.title == title:
                return e
        return None

    def _get_entries(self, wiki_client, since_date=None):
        entries = wiki_client.service.getBlogEntries(wiki_client.auth, wiki_client.space_name)
        if since_date:
            date_filter = lambda e: e.publishDate >= since_date
            entries = filter(date_filter, entries)
        return entries

    def _create_entry(self, src_entry, trg_entry_id=None):
        entry = self.trg_client.client.factory.create('ns0:RemoteBlogEntry')
        entry.title = src_entry.title
        entry.space = self.trg_client.space_name
        entry.content = src_entry.content
        entry.publishDate = src_entry.publishDate
        entry.content = src_entry.content
        entry.version = "0"
        entry.id = "0" if not trg_entry_id else trg_entry_id
        entry.permissions = "0"
        return entry

def main():
    if len(sys.argv) < 4:
        print "Usage: clone_wiki_news from-profile to-profile mm/dd/yyyy"
        exit(1)

    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel(logging.DEBUG)
    logging.getLogger('suds').setLevel(logging.INFO)

    cloner = CloneNews(sys.argv[1], sys.argv[2])
    cloner.clone_news(datetime.strptime(sys.argv[3], '%m/%d/%Y') if len(sys.argv) > 3 else None)

if __name__ == '__main__':
    main()
