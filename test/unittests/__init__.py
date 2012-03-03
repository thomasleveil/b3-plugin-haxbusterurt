import unittest
import logging
from b3 import TEAM_UNKNOWN
from b3.config import XmlConfigParser
from b3.fake import FakeClient

from b3.parsers.iourt41 import Iourt41Parser
from b3.plugins.admin import AdminPlugin


class Iourt41TestCase(unittest.TestCase):
    """
    Test case that is suitable for testing iourt41 parser specific features
    """

    @classmethod
    def setUpClass(cls):
        # less logging
        logging.getLogger('output').setLevel(logging.CRITICAL)

        from b3.parsers.q3a.abstractParser import AbstractParser
        from b3.fake import FakeConsole
        AbstractParser.__bases__ = (FakeConsole,)
        # Now parser inheritance hierarchy is :
        # Iourt41Parser -> AbstractParser -> FakeConsole -> Parser


    def setUp(self):
        # create a BF3 parser
        self.parser_conf = XmlConfigParser()
        self.parser_conf.loadFromString("""
            <configuration>
                <settings name="messages">
                <set name="kicked_by">$clientname was kicked by $adminname $reason</set>
                <set name="kicked">$clientname was kicked $reason</set>
                <set name="banned_by">$clientname was banned by $adminname $reason</set>
                <set name="banned">$clientname was banned $reason</set>
                <set name="temp_banned_by">$clientname was temp banned by $adminname for $banduration $reason</set>
                <set name="temp_banned">$clientname was temp banned for $banduration $reason</set>
                <set name="unbanned_by">$clientname was un-banned by $adminname $reason</set>
                <set name="unbanned">$clientname was un-banned $reason</set>
            </settings>
            </configuration>
        """)
        self.console = Iourt41Parser(self.parser_conf)
        self.console.startup()

        # load the admin plugin
        self.adminPlugin = AdminPlugin(self.console, '@b3/conf/plugin_admin.xml')
        self.adminPlugin.onStartup()

        # make sure the admin plugin obtained by other plugins is our admin plugin
        def getPlugin(name):
            if name == 'admin':
                return self.adminPlugin
            else:
                return self.console.getPlugin(name)
        self.console.getPlugin = getPlugin

        # prepare a few players
        self.joe = FakeClient(self.console, name="Joe", guid="00000000000000000000000000000001", groupBits=1, team=TEAM_UNKNOWN)
        self.simon = FakeClient(self.console, name="Simon", guid="00000000000000000000000000000002", groupBits=0, team=TEAM_UNKNOWN)
        self.reg = FakeClient(self.console, name="Reg", guid="00000000000000000000000000000003", groupBits=4, team=TEAM_UNKNOWN)
        self.moderator = FakeClient(self.console, name="Moderator", guid="00000000000000000000000000000004", groupBits=8, team=TEAM_UNKNOWN)
        self.admin = FakeClient(self.console, name="Level-40-Admin", guid="00000000000000000000000000000005", groupBits=16, team=TEAM_UNKNOWN)
        self.superadmin = FakeClient(self.console, name="God", guid="00000000000000000000000000000000", groupBits=128, team=TEAM_UNKNOWN)

        # more logging
        logging.getLogger('output').setLevel(logging.DEBUG)