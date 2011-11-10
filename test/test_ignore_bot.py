# -*- encoding: utf-8 -*-
from test import prepare_fakeparser_for_tests, set_clients_ports
prepare_fakeparser_for_tests()

from b3.fake import fakeConsole, FakeClient, superadmin
from haxbusterurt import HaxbusterurtPlugin
from b3.config import XmlConfigParser


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


set_clients_ports({'0': '321', '1': '654'})

maxime = FakeClient(fakeConsole, name="BOT4", exactName="BOT4", ip="0.0.0.0", guid="BOT4")
maxime.connects('1')