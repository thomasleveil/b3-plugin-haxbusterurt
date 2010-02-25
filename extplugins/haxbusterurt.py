#
# BigBrotherBot(B3) (www.bigbrotherbot.com)
# Copyright (C) 2009 Courgette
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# CHANGELOG
# 15/12/2009 - 0.1 - Courgette
#    * detects when guid is not a ioUrT guid nor a Q3 guid
#    * upon client connect with bad guid :
#        o give the player a notice so it can be found in echelon
#        o pm ingame admins
#    * upon admin connection : pm admin of eventual ingame hackers
# 15/12/2009 - 0.2 - Courgette
#    * will fire event b3.events.EVT_BAD_GUID when bad guid is found so other
#      plugins can react to such event
#    * when plugin is enabled (after having been disabled) it checks all new players
#    * check all connected players at start
#    * make sure a given player is checked only once
# 25/02/2010 - 1.0 - Courgette
#    * consider players whose guid equals their ip to have unlegitimates guid
#

__author__  = 'Courgette <courgette@ubu-team.org>'
__version__ = '0.3'

import b3
import re
import threading
import b3.events
import b3.plugin
import b3.functions

#--------------------------------------------------------------------------------------------------
class HaxbusterurtPlugin(b3.plugin.Plugin):
    requiresConfigFile = False
    _adminPlugin = None
    _reValidGuid = re.compile('^[A-F0-9]{32}$')
    _msgDelay = 30 # seconds to wait after an admin connect before sending him messages
    _adminLevel = 60

    def onStartup(self):
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            return False

        # create a new type of event so other plugin can react when we 
        # detect bad guid
        self.console.Events.createEvent('EVT_BAD_GUID', 'Bad guid detected')
        
        self._adminLevel = self._adminPlugin.config.getint('settings', 'admins_level')
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        t = threading.Timer(2, self.checkAllClients)
        t.start()


    def onLoadConfig(self):
        # @todo: config could define a penalty to inflict to bad guid (kick, tempban, ban, etc)
        pass


    def enable(self):
        b3.plugin.Plugin.enable(self)
        self.checkAllClients()
            
            
    def onEvent(self, event):
        if not event.client:
            return
    
        if event.type == b3.events.EVT_CLIENT_AUTH:
            self.checkGuid(event.client)
            if event.client.maxLevel >= self._adminLevel:
                self.onAdminConnect(event.client)
        
        
    def onAdminConnect(self, client):
        self.debug("admin connected")
        haxorNames = []
        for c in self.console.clients.getClientsByLevel():
            if c == client:
                continue
            if c.var(self, 'haxBusted').value == True:
                haxorNames.append(c.name)
        if len(haxorNames) > 0:
            t = threading.Timer(self._msgDelay,
                        client.message, ("^2Haxor detected: ^3%s" % (', '.join(haxorNames)) ,))
            t.start()
        else:
            self.debug('no haxor guid currently connected')
                     
                     
    def checkAllClients(self):
        self.info("checking all new clients guid")
        for c in self.console.clients.getClientsByLevel():
            self.checkGuid(c)
                
                
    def checkGuid(self, client):
        guid = client.guid
        if guid is None:
            self.debug('That\'s weird, client @%s has no guid' % client.id)
            return
        
        isHaxor = client.var(self, 'haxBusted').value
        if isHaxor is not None:
            self.debug('%s was checked before : %s' % (client.name, isHaxor))
            return
        
        # check normal ioUrbanTerror guid
        if self._reValidGuid.search(guid) is not None:
            client.setvar(self, 'haxBusted', False)
            self.debug('%s is a valid ioUrT guid' % (guid))
            return
        
        # now we got a contestable guid
        client.setvar(self, 'haxBusted', True)
        self.info("player @%s (%s) has a contestable guid : [%s]" % (client.id, client.ip, guid))
        self.console.queueEvent(b3.events.Event(b3.events.EVT_BAD_GUID, guid, client)) 
        client.notice("weird guid detected", None)
        
        for c in self.console.clients.getClientsByLevel(min=self._adminLevel):
            if c == client:
                continue
            c.message('%s^7 is probably hacking. His guid is [^3%s^7]' % (client.exactName, guid))
        


    
if __name__ == '__main__':
    from b3.fake import fakeConsole
    from b3.fake import FakeClient
    from b3.fake import superadmin
    from b3.fake import moderator

    import time
    
    class FakePlugin(b3.plugin.Plugin):
        requiresConfigFile = False
        def onEvent(self, event):
            print "\tFakePlugin received event %s: guid:%s, player:%s" % (event.type, event.data, event.client.name)
    
    
    maxime = FakeClient(fakeConsole, name="Maxime", exactName="Maxime",
                         ip="123.123.123.123", guid="ABCDEF0123456789ABCDEF0123456789") 
    maxime.connects(2)
    time.sleep(1)
    
    
    print '-------- instanciating Haxbuster ------------'
    p = HaxbusterurtPlugin(fakeConsole)
    fakeConsole._plugins['haxbuster'] = p
    p._msgDelay = 2
    p.onStartup()
    time.sleep(3)

    fakePlugin = FakePlugin(fakeConsole)
    fakePlugin.registerEvent(b3.events.EVT_BAD_GUID)


    time.sleep(1)
    
    
    player2 = FakeClient(fakeConsole, name="James", exactName="James",
                         ip="112.111.113.11", guid="112.111.113.11") 
    player2.connects(3)
    time.sleep(1)
    
 
    player2 = FakeClient(fakeConsole, name="K!773R", exactName="K!773R",
                         ip="12.12.113.11", guid="/me is hacking") 
    player2.connects(14)
    time.sleep(1)
 
 
    player3 = FakeClient(fakeConsole, name="ownyou", exactName="ownyou",
                         ip="12.12.113.11", guid="12.123.113.255") 
    player3.connects(12)
    time.sleep(1)
    
    
    superadmin.connects(1)
    time.sleep(3)
    
    
    player4 = FakeClient(fakeConsole, name="pownd", exactName="pownd",
                        ip="12.12.113.11", guid="mljsfdmljsdfqm") 
    time.sleep(1)
    
    moderator.connects(8)
    time.sleep(3)
    
    superadmin.says('!disable haxbuster')
    superadmin.says('!enable haxbuster')
    
    maxime.disconnects()
    maxime.connects(9)
    time.sleep(1)
    
    superadmin.disconnects()
    superadmin.connects(1)
    time.sleep(5)