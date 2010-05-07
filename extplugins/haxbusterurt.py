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
# 06/05/2010 - 1.1 - Courgette
#    * add a config file (optional)
#    * you can choose in the config if you consider a guid which is equals to
#      the IP legitimate or not
#    * you can choose in the config if you want to kick bad guid
# 07/05/2010 - 1.2 - Courgette
#    * rename the config file option allow_guid_equals_to_ip to allow_empty_guid
#      to make more sense. (B3 uses players'IP for guid if cl_guid is empty)
#    * cache check result for client having empty guid
#    * Does not accept empty cl_guid by default

__author__  = 'Courgette <courgette@ubu-team.org>'
__version__ = '1.2'

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
    acceptEmptyGuid = False
    doKick = False

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
        self.debug('loading config')
        try:
            self.acceptEmptyGuid = self.config.getboolean('settings', 'allow_empty_guid')
        except:
            self.acceptEmptyGuid = True
        self.debug('accept empty Guid ? : %s' % self.acceptEmptyGuid)
        
        try:
            self.doKick = self.config.getboolean('settings', 'kick_bad_guid')
        except:
            self.doKick = False
        self.debug('kick bad guid ? : %s' % self.doKick)


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
        if self.isBadGuid(client):
            # now we got a contestable guid
            self.info("player @%s (%s) has a contestable guid : [%s]" % (client.id, client.ip, client.guid))
            self.console.queueEvent(b3.events.Event(b3.events.EVT_BAD_GUID, client.guid, client)) 
            client.notice("weird guid detected", None)
            
            for c in self.console.clients.getClientsByLevel(min=self._adminLevel):
                if c == client:
                    continue
                c.message('%s^7 is probably hacking. His guid is [^3%s^7]' % (client.exactName, client.guid))
            
            if self.doKick:
                self.info('kicking client because of its GUID')
                client.kick('Not welcome on this server', keyword="haxbusterurt", silent=True)
        
    def isBadGuid(self, client):
        ## have we checked this client before ?
        cachedResult = client.var(self, 'haxBusted').value
        if cachedResult is not None:
            self.debug('%s was checked before : %s' % (client.name, cachedResult))
            return cachedResult
        
        ## empty guid client property o_O should not happen
        if client.guid is None:
            self.warn('That\'s weird, client @%s has no guid' % client.id)
            return False
        
        ## guid == ip --> reveals a clients that connects with an empty cl_guid
        if hasattr(client, 'ip') and client.ip == client.guid:
            self.info('player @%s (%s) has an empty guid' % (client.id, client.ip))
            client.setvar(self, 'haxBusted', not self.acceptEmptyGuid)
            return not self.acceptEmptyGuid
        
        # check normal ioUrbanTerror guid
        if self._reValidGuid.search(client.guid) is not None:
            client.setvar(self, 'haxBusted', False)
            self.info('%s is a valid ioUrT guid' % (client.guid))
            return False
        else:
            self.info('%s is a not a valid ioUrT guid' % (client.guid))
            client.setvar(self, 'haxBusted', True)
            return True
        
    
if __name__ == '__main__':
    from b3.fake import fakeConsole
    from b3.fake import FakeClient
    from b3.fake import superadmin
    from b3.fake import moderator

    import time
    
    from b3.config import XmlConfigParser
    
    conf = XmlConfigParser()
    conf.setXml("""\
    <configuration plugin="haxbusterurt">
        <settings name="settings">
            <!-- Do you accept clients with an empty cl_guid ? -->
            <set name="allow_empty_guid">no</set>
            <!-- Do you want to kick players with bad guid ? -->
            <set name="kick_bad_guid">yes</set>
        </settings>
    </configuration>

    """)
    
    
    class FakePlugin(b3.plugin.Plugin):
        requiresConfigFile = False
        def onEvent(self, event):
            print "\tFakePlugin received event %s: guid:%s, player:%s" % (event.type, event.data, event.client.name)
    
    
    maxime = FakeClient(fakeConsole, name="Maxime", exactName="Maxime",
                         ip="123.123.123.123", guid="ABCDEF0123456789ABCDEF0123456789") 
    maxime.connects(2)
    time.sleep(1)
    
    
    print '-------- instanciating Haxbuster ------------'
    p = HaxbusterurtPlugin(fakeConsole, conf)
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
    
    p.isBadGuid(player2)
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