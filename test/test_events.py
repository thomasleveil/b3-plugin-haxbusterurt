# -*- encoding: utf-8 -*-
from test import prepare_fakeparser_for_tests, set_clients_ports
import b3

prepare_fakeparser_for_tests()

from b3.fake import fakeConsole, FakeClient, superadmin
from haxbusterurt import HaxbusterurtPlugin
from b3.config import XmlConfigParser


class FakePlugin(b3.plugin.Plugin):
    requiresConfigFile = False
    def onEvent(self, event):
        print "\tFakePlugin received event [%s]: data: %s, player: %s" % (fakeConsole.getEventName(event.type), event.data, event.client.name)



conf = XmlConfigParser()
conf.loadFromString("""
<configuration plugin="haxbusterurt">
	<settings name="settings">
	</settings>
</configuration>
""")

p = HaxbusterurtPlugin(fakeConsole, conf)
p.onLoadConfig()
p.onStartup()

fakePlugin = FakePlugin(fakeConsole)
fakePlugin.registerEvent(b3.events.EVT_BAD_GUID)
fakePlugin.registerEvent(b3.events.EVT_1337_PORT)

set_clients_ports({'0': '321', '1': '1337'})



maxime = FakeClient(fakeConsole, name="Maxime", exactName="Maxime", ip="123.123.123.123", guid="BAAAAAAD")
maxime.connects('1')