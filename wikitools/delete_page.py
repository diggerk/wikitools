import sys
import logging

from wikitools.common import WikiClient


logger = logging.getLogger(__name__)


class DeletePage(object):
    def __init__(self, profile):
        self.client = WikiClient(profile)

        self.pages_by_names = self.client.client.__unicode__().find('getPage(xs:string in0, xs:string in1, xs:string in2') > 0
        self.attachmens_without_page_id = self.client.client.__unicode__().find('addAttachment(xs:string in0, ns0:RemoteAttachment') > 0

        self.pages = self.client.service.getPages(
            self.client.auth, self.client.space_name)

    def delete_page(self, page_name):
        page = self._get_page(self.pages, page_name)
        if page is None:
            logger.error("Can't find page %s in space %s", page_name, self.client.space_name)
            raise Exception("Can't find page %s in space %s", page_name, self.client.space_name)
        for child in self.client.service.getChildren(self.client.auth, page.id):
            self.delete_page(child.title)
        self.client.service.removePage(self.client.auth, page.id)
        logger.info("Successfully deleted page '%s'", page.title)

    def _get_page(self, pages, page_name):
        for page in pages:
            if page.title == page_name:
                return page
        return None

def main():
    if len(sys.argv) < 3:
        print "Usage: python delete_page.py profile-name page-title"
        exit(1)

    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel(logging.DEBUG)
    logging.getLogger('suds').setLevel(logging.INFO)

    cloner = DeletePage(sys.argv[1])
    cloner.delete_page(sys.argv[2])

if __name__ == '__main__':
    main()
