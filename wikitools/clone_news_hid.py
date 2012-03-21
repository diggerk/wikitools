import sys
import logging
from datetime import datetime

from clone_news import CloneNews


logger = logging.getLogger(__name__)


class CloneNewsHidingBlock(CloneNews):
    def __init__(self, from_profile, to_profile, separator, title_keyword):
        super(CloneNewsHidingBlock, self).__init__(from_profile, to_profile)
        self.separator = separator
        self.title_keyword = title_keyword.lower() if title_keyword else None
    def _create_entry(self, src_entry, trg_entry_id=None):
        if self.title_keyword and src_entry.title.lower().find(self.title_keyword) == -1:
            logger.info("Skipping news '%s' as keyword '%s' is not presented in the title",
                src_entry.title, self.title_keyword)
            return None
        e = super(CloneNewsHidingBlock, self)._create_entry(src_entry, trg_entry_id)
        if e.content and e.content.find(self.separator) != -1:
            e.content = e.content[:e.content.index(self.separator)]
        return e

def main():
    if len(sys.argv) < 4:
        print "Usage: clone_wiki_news_hid from-profile to-profile mm/dd/yyyy [separator] [title_keyword]"
        exit(1)

    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel(logging.DEBUG)
    logging.getLogger('suds').setLevel(logging.INFO)

    separator = sys.argv[4] if len(sys.argv) > 4 else '----'
    title_keyword = sys.argv[5] if len(sys.argv) > 5 else None
    cloner = CloneNewsHidingBlock(sys.argv[1], sys.argv[2], separator, title_keyword)
    cloner.clone_news(datetime.strptime(sys.argv[3], '%m/%d/%Y') if len(sys.argv) > 3 else None)

if __name__ == '__main__':
    main()
