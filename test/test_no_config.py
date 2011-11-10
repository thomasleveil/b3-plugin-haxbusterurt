# -*- encoding: utf-8 -*-
from test import prepare_fakeparser_for_tests
prepare_fakeparser_for_tests()

from b3.fake import fakeConsole
from haxbusterurt import HaxbusterurtPlugin, PENALTY_DEFAULT

p = HaxbusterurtPlugin(fakeConsole)
p.onLoadConfig()
p.onStartup()

print "\n\n========================================="
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