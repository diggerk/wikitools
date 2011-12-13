Set of scripts automating operations with 
[Confluence Wiki](http://www.atlassian.com/software/confluence).

Configuration
=============
Create ~/.wikitools file with multiple sections describing number of
Wiki instances and/or spaces. Example:

    [mxmo_internal]
    uri=https://wiki.mycompanysite.net/rpc/soap-axis/confluenceservice-v1?wsdl
    username=myusername
    password=mysecret
    space=MXMO

    [mxmo_customer]
    uri=https://wiki.mycustomersite.net/rpc/soap-axis/confluenceservice-v1?wsdl
    username=anothername
    password=anothersecret
    space=MMXX

Cloning hierarchy of pages and attachments
==========================================
clone_page.py -- clone Wiki page into a differnt Wiki instance or space.
Supports cloning of child pages and attachments. Can be used repeatedly 
to update cloned pages.

Now to copy page "System Design" from the internal Wiki to a customer Wiki
I can issue this command:

    python clone_page.py mxmo_internal "System Design" mxmo_customer

This will clone the given page itself together with all it's children and 
attachments, including transitive data.
