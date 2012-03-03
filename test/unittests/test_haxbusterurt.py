from mock import Mock, patch
import threading
from haxbusterurt import HaxbusterurtPlugin
from b3.config import XmlConfigParser
from test.unittests import Iourt41TestCase

class Test_ktkwftmkemfew(Iourt41TestCase):

    @classmethod
    def setUpClass(cls):
        super(Test_ktkwftmkemfew, cls).setUpClass()
        cls.timer_patcher = patch.object(threading, 'Timer')
        cls.timer_patcher.start()

    @classmethod
    def tearDownClass(cls):
        super(Test_ktkwftmkemfew, cls).tearDownClass()
        cls.timer_patcher.stop()

    def setUp(self):
        super(Test_ktkwftmkemfew, self).setUp()

        def getPlayersPort(me):
            data = {}
            for cid, client in self.console.clients.items():
                if hasattr(client, 'port'):
                    data[client.cid] = client.port
            return data
        HaxbusterurtPlugin.getPlayersPort = getPlayersPort


    def test_ktkwftmkemfew(self):
        conf = XmlConfigParser()
        conf.loadFromString("""
            <configuration plugin="haxbusterurt">
                <settings name="settings">
                    <set name="allow_empty_guid">yes</set>
                    <set name="bad_guid_penalty">permban</set>
                </settings>
            </configuration>
        """)
        p = HaxbusterurtPlugin(self.console, conf)
        p.onStartup()
        p.onLoadConfig()

        self.joe._guid="08:51:01ktkwftmkemfew307/11/08"
        self.joe.ban = Mock(wraps=self.joe.ban)
        self.joe.connects(cid='1')
        self.assertEqual(1, self.joe.ban.call_count)

        self.moderator._guid = "123456789012345678901234567890AB"
        self.moderator.ban = Mock(wraps=self.moderator.ban)
        self.moderator.connects(cid='3')
        self.assertFalse(self.moderator.ban.called)



    def test_bad_guid(self):
        conf = XmlConfigParser()
        conf.loadFromString("""
            <configuration plugin="haxbusterurt">
                <settings name="settings">
                    <set name="allow_empty_guid">yes</set>
                    <set name="bad_guid_penalty">tempban</set>
                </settings>
            </configuration>
        """)
        p = HaxbusterurtPlugin(self.console, conf)
        p.onStartup()
        p.onLoadConfig()

        self.joe._guid="bad_guid"
        self.joe.tempban = Mock(wraps=self.joe.tempban)
        self.joe.connects(cid='1')
        self.assertEqual(1, self.joe.tempban.call_count)

        self.moderator._guid = "123456789012345678901234567890AB"
        self.moderator.tempban = Mock(wraps=self.moderator.tempban)
        self.moderator.connects(cid='3')
        self.assertFalse(self.moderator.tempban.called)


    def test_1337_port(self):
        conf = XmlConfigParser()
        conf.loadFromString("""
            <configuration plugin="haxbusterurt">
                <settings name="settings">
                    <set name="allow_empty_guid">yes</set>
                    <set name="1337_port_penalty">kick</set>
                </settings>
            </configuration>
        """)
        p = HaxbusterurtPlugin(self.console, conf)
        p.onStartup()
        p.onLoadConfig()

        self.joe.port = "1337"
        self.joe.kick = Mock(wraps=self.joe.kick)
        self.joe.connects(cid='1')
        self.assertEqual(1, self.joe.kick.call_count)

        self.moderator.port = "12454"
        self.moderator.kick = Mock(wraps=self.moderator.kick)
        self.moderator.connects(cid='3')
        self.assertFalse(self.moderator.kick.called)