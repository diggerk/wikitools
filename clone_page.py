import sys
import logging

from wikitools.common import WikiClient


logger = logging.getLogger(__name__)


class ClonePages(object):
    def __init__(self, from_profile, to_profile):
        self.src_client = WikiClient(from_profile)
        self.trg_client = WikiClient(to_profile)

        self.src_client.pages_by_names = self.src_client.client.__unicode__().find('getPage(xs:string in0, xs:string in1, xs:string in2') > 0
        self.trg_client.pages_by_names = self.trg_client.client.__unicode__().find('getPage(xs:string in0, xs:string in1, xs:string in2') > 0

        self.trg_client.attachmens_without_page_id = self.trg_client.client.__unicode__().find('addAttachment(xs:string in0, ns0:RemoteAttachment') > 0

        self.src_pages = self.src_client.service.getPages(
            self.src_client.auth, self.src_client.space_name)
        self.trg_pages = self.trg_client.service.getPages(
            self.trg_client.auth, self.trg_client.space_name)

        space = self.trg_client.service.getSpace(self.trg_client.auth, self.trg_client.space_name)
        self.trg_home_page = filter(lambda p: p.id == space.homePage, self.trg_pages)[0]

        self.created_pages = {}

    def clone_page(self, src_page_name, trg_page_name=None):
        if not trg_page_name:
            trg_page_name = src_page_name

        src_page = self._get_page(self.src_pages, src_page_name)
        if src_page is None:
            logger.error("Can't find page %s in space %s", src_page_name, self.src_client.space_name)
            raise Exception("Can't find page %s in space %s", src_page_name, self.src_client.space_name)

        trg_page = self._get_page(self.trg_pages, trg_page_name, True)
        if trg_page is None:
            trg_page = self._create_page(src_page, self.trg_home_page)

        logger.info("Cloning page '%s' from %s to %s", src_page_name, src_page.id, trg_page.id)
        self._clone_page(src_page, trg_page)
        for child in self.src_client.service.getChildren(self.src_client.auth, src_page.id):
            trg_child = self._get_page(self.trg_pages, child.title, True)
            if not trg_child:
                logger.info("Creating child page '%s'", child.title)
                trg_child = self._create_page(child, trg_page)
            if trg_child.parentId != trg_page.id:
                logger.warning("Skip child page '%s' as it's beloning to a different parent in trg Wiki",
                    child.title)
            else:
                logger.info("Cloning child page '%s'", child.title)
                self.clone_page(child.title)

    def _get_page_details(self, wiki_client, page_info):
        if wiki_client.pages_by_names:
            return wiki_client.service.getPage(wiki_client.auth, page_info.space, page_info.title)
        else:
            return wiki_client.service.getPage(wiki_client.auth, page_info.id)

    def _create_page(self, src_page_info, trg_parent):
        src_page = self._get_page_details(self.src_client, src_page_info)
        page = self.trg_client.client.factory.create('ns0:RemotePage')
        page.title = src_page.title
        page.content = src_page.content
        page.parentId = trg_parent.id
        page.space = trg_parent.space
        page.version = "0"
        page.current = True
        page.contentStatus = "current"
        page.homePage = False
        page.id = "0"
        page.permissions = "0"
        page = self.trg_client.service.storePage(self.trg_client.auth, page)
        self.created_pages[page.title] = page
        return page

    def _clone_page(self, src_page_info, trg_page_info):
        src_page = self._get_page_details(self.src_client, src_page_info)

        trg_page = self._get_page_details(self.trg_client, trg_page_info)
        trg_page.content = src_page.content

        if trg_page.modified >= src_page.modified:
            logger.info("Page '%s' is already up to date", trg_page.title)
        else:
            update_options = self.trg_client.client.factory.create('ns0:RemotePageUpdateOptions')
            update_options.versionComment = 'Clone page content from the src Wiki'
            update_options.minorEdit = False

            updated_page = self.trg_client.service.updatePage(self.trg_client.auth, trg_page, update_options)
            logger.info("Successfully created version %s of page '%s'", updated_page.version, updated_page.title)

        self._clone_attachments(src_page, trg_page)

    def _clone_attachments(self, src_page, trg_page):
        trg_atts = self.trg_client.service.getAttachments(self.trg_client.auth, trg_page.id)
        for att in self.src_client.service.getAttachments(self.src_client.auth, src_page.id):
            trg_att = None
            for a in trg_atts:
                if a.fileName == att.fileName:
                    trg_att = a
                    break
            if trg_att is None:
                logger.info("Cloning attachment %s", att.fileName)
                trg_att = self.trg_client.client.factory.create('ns0:RemoteAttachment')
                trg_att.fileName = att.fileName
                trg_att.title = att.title
                trg_att.contentType = att.contentType
                trg_att.comment = att.comment
                trg_att.fileSize = att.fileSize
                trg_att.id = "0"
                trg_att.pageId = trg_page.id
                data = self.src_client.service.getAttachmentData(self.src_client.auth,
                    src_page.id, att.fileName, "0")
                if self.trg_client.attachmens_without_page_id:
                    self.trg_client.service.addAttachment(self.trg_client.auth,
                        trg_att, data)
                else:
                    self.trg_client.service.addAttachment(self.trg_client.auth,
                        trg_page.id, trg_att, data)

    def _get_page(self, pages, page_name, check_created=False):
        if check_created and page_name in self.created_pages:
            return self.created_pages[page_name]
        for page in pages:
            if page.title == page_name:
                return page
        return None


if len(sys.argv) < 4:
    print "Usage: python clone_page.py from-profile from-page to-profile [to-page]"
    exit(1)

logging.root.addHandler(logging.StreamHandler())
logging.root.setLevel(logging.DEBUG)
logging.getLogger('suds').setLevel(logging.INFO)

cloner = ClonePages(sys.argv[1], sys.argv[3])
cloner.clone_page(sys.argv[2], sys.argv[4] if len(sys.argv) > 4 else None)
