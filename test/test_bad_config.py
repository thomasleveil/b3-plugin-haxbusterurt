# -*- encoding: utf-8 -*-
from test import prepare_fakeparser_for_tests
prepare_fakeparser_for_tests()

from b3.fake import fakeConsole
from haxbusterurt import HaxbusterurtPlugin, PENALTY_DEFAULT
from b3.config import XmlConfigParser



conf1 = XmlConfigParser()
conf1.loadFromString("""
<configuration plugin="haxbusterurt"/>
""")

p = HaxbusterurtPlugin(fakeConsole, conf1)
p.onLoadConfig()
p.onStartup()

print "\n\n======= TEST empty config ==============="
try:
    assert p._adminLevel == 60
    assert p.acceptEmptyGuid == False
    assert p.bad_guid_penalty == PENALTY_DEFAULT
    assert p.port_1337_penalty == PENALTY_DEFAULT
    assert p.tempban_duration == '2d'
except AssertionError:
    print "FAIL"
    raise
print "PASS"




conf2 = XmlConfigParser()
conf2.loadFromString("""
<configuration plugin="haxbusterurt">
	<settings name="settings">
        <set name="notify_players_from_level">qsdf</set>
		<set name="allow_empty_guid">maybe</set>
		<set name="bad_guid_penalty">slap</set>
		<set name="1337_port_penalty"></set>
        <set name="tempban_duration">qsdf</set>
	</settings>
</configuration>
""")

p = HaxbusterurtPlugin(fakeConsole, conf2)
p.onLoadConfig()
p.onStartup()

print "\n\n======== TEST incorrect values =========="
try:
    assert p._adminLevel == 60
    assert p.acceptEmptyGuid == False
    assert p.bad_guid_penalty == PENALTY_DEFAULT
    assert p.port_1337_penalty == PENALTY_DEFAULT
    assert p.tempban_duration == '2d'
except AssertionError:
    print "FAIL"
    raise
print "PASS"

