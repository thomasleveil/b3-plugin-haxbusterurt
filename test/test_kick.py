# -*- encoding: utf-8 -*-
from test import prepare_fakeparser_for_tests, set_clients_ports
import time

prepare_fakeparser_for_tests()

from b3.fake import fakeConsole, FakeClient
from haxbusterurt import HaxbusterurtPlugin, PENALTY_NONE, PENALTY_KICK
from b3.config import XmlConfigParser



set_clients_ports({'0': '321', '1': '1337'})


conf = XmlConfigParser()
conf.loadFromString("""
<configuration plugin="haxbusterurt">
	<settings name="settings">
	    <set name="bad_guid_penalty">kick</set>
	</settings>
</configuration>
""")
p = HaxbusterurtPlugin(fakeConsole, conf)
p.onLoadConfig()
assert p.bad_guid_penalty == PENALTY_KICK
assert p.port_1337_penalty == PENALTY_NONE
p.onStartup()
maxime = FakeClient(fakeConsole, name="Maxime", exactName="Maxime", ip="123.123.123.123", guid="BAAAAAAD")
maxime.connects('1')


time.sleep(5)
print "\n\n=============================================================================="

conf = XmlConfigParser()
conf.loadFromString("""
<configuration plugin="haxbusterurt">
	<settings name="settings">
	    <set name="1337_port_penalty">kick</set>
	</settings>
</configuration>
""")
p = HaxbusterurtPlugin(fakeConsole, conf)
p.onLoadConfig()
assert p.bad_guid_penalty == PENALTY_NONE
assert p.port_1337_penalty == PENALTY_KICK
p.onStartup()
maxime = FakeClient(fakeConsole, name="Maxime", exactName="Maxime", ip="123.123.123.123", guid="BAAAAAAD")
maxime.connects('1')