#
# BigBrotherBot(B3) (www.bigbrotherbot.net)
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
# 03/03/2011 - 1.3 - Courgette
#    * ingnore bots when checking clients
# 05/03/2011 - 1.3.1 - Courgette
#    * better bot detection
# 10/11/2011 - 1.4 - Courgette
#    * can detect players connecting from port 1337
#    * can define in config which kind of penalty apply (none, kick, tempban, permban)
#
__author__  = 'Courgette <courgette@bigbrotherbot.net>'
__version__ = '1.4'

import b3
import re
import threading
import b3.events
import b3.plugin
from b3.functions import time2minutes, minutesStr

PENALTY_NONE = 'none'
PENALTY_KICK = 'kick'
PENALTY_TEMPBAN = 'tempban'
PENALTY_PERMBAN = 'permban'
PENALTY_DEFAULT = PENALTY_NONE
PENALTIES = {
    PENALTY_NONE: 1,
    PENALTY_KICK: 2,
    PENALTY_TEMPBAN: 3,
    PENALTY_PERMBAN: 4,
}

class HaxbusterurtConfigError(Exception): pass

#--------------------------------------------------------------------------------------------------
class HaxbusterurtPlugin(b3.plugin.Plugin):
    requiresConfigFile = False
    _adminPlugin = None
    _reValidGuid = re.compile('^[A-F0-9]{32}$')
    _msgDelay = 30 # seconds to wait after an admin connect before sending him messages
    _adminLevel = 60
    acceptEmptyGuid = False
    bad_guid_penalty = PENALTY_NONE
    port_1337_penalty = PENALTY_NONE
    tempban_duration = '2d'

    def onStartup(self):
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            return False

        # create a new type of event so other plugin can react when we 
        # detect hacks
        self.console.Events.createEvent('EVT_BAD_GUID', 'Bad guid detected')
        self.console.Events.createEvent('EVT_1337_PORT', '1337 port detected')

        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        t = threading.Timer(2, self.checkAllClients)
        t.start()


    def onLoadConfig(self):
        self.debug('loading config')

        try:
            self._adminLevel = self.config.getint('settings', 'notify_players_from_level')
        except Exception, err:
            self.warning(err)
        self.info('notify_players_from_level : %s' % self._adminLevel)

        try:
            self.acceptEmptyGuid = self.config.getboolean('settings', 'allow_empty_guid')
        except Exception, err:
            self.warning(err)
        self.info('accept empty Guid ? : %s' % self.acceptEmptyGuid)
        
        try:
            penalty = self.config.get('settings', 'bad_guid_penalty')
            if penalty not in PENALTIES:
                raise HaxbusterurtConfigError("bad penalty keyword for bad_guid_penalty. Using default instead. Expecting on of \"%s\"" % ', '.join(PENALTIES.keys()))
            else:
                self.bad_guid_penalty = penalty.lower()
        except Exception, err:
            self.warning(err)
            self.bad_guid_penalty = PENALTY_DEFAULT
        self.info('"bad guid" penalty : %s' % self.bad_guid_penalty)

        try:
            penalty = self.config.get('settings', '1337_port_penalty')
            if penalty not in PENALTIES:
                raise HaxbusterurtConfigError("bad penalty keyword for 1337_port_penalty. Using default instead. Expecting on of \"%s\"" % ', '.join(PENALTIES.keys()))
            else:
                self.port_1337_penalty = penalty.lower()
        except Exception, err:
            self.warning(err)
            self.port_1337_penalty = PENALTY_DEFAULT
        self.info('1337 port penalty : %s' % self.port_1337_penalty)

        try:
            duration = self.config.get('settings', 'tempban_duration')
            duration_minutes = time2minutes(duration)
            if duration_minutes <= 0:
                raise HaxbusterurtConfigError("bad value for tempban_duration \"%s\"" % duration)
            self.tempban_duration = duration_minutes
        except Exception, err:
            self.warning(err)
        self.info('tempban duration : %s' % minutesStr(self.tempban_duration))


    def enable(self):
        b3.plugin.Plugin.enable(self)
        self.checkAllClients()
            
            
    def onEvent(self, event):
        if not event.client:
            return
    
        if event.type == b3.events.EVT_CLIENT_AUTH:
            self.checkHacks(event.client)
            if event.client.maxLevel >= self._adminLevel:
                self.onAdminConnect(event.client)
        
        
    def onAdminConnect(self, client):
        self.debug("admin connected")
        haxorNames = []
        for c in self.console.clients.getClientsByLevel():
            if c == client:
                continue
            if c.var(self, 'haxBusted').value:
                haxorNames.append(c.name)
        if len(haxorNames) > 0:
            t = threading.Timer(self._msgDelay,
                        client.message, ("^2Haxor detected: ^3%s" % (', '.join(haxorNames)) ,))
            t.start()
        else:
            self.debug('no haxor currently connected')
                     
                     
    def checkAllClients(self):
        self.info("checking all new clients guid")
        clients_port = self.getPlayersPort()
        for c in self.console.clients.getClientsByLevel():
            self.checkHacks(c, clients_port)

    def checkHacks(self, client, clients_port=None):
        """check if client uses hacks"""
        penalty = PENALTY_NONE
        reasons = []
        busted = False

        if self.isBadGuid(client):
            # now we got a contestable guid
            busted = True
            reasons.append('bad guid')
            self.info("player @%s (%s) has a contestable guid : [%s]" % (client.id, client.ip, client.guid))
            self.console.queueEvent(b3.events.Event(b3.events.EVT_BAD_GUID, data=client.guid, client=client))
            client.notice("weird guid detected", None)
            self.tell_admins_except_one(client, '%s^7 (@%s) is probably hacking. His guid is [^3%s^7]' % (client.exactName, client.id, client.guid))
            if self.bad_guid_penalty and PENALTIES[self.bad_guid_penalty] > PENALTIES[penalty]:
                penalty = self.bad_guid_penalty

        if self.is_1337_port(client, clients_port):
            # client connecting from 1337 port
            busted = True
            reasons.append('1337 port')
            self.info("player @%s (%s) is connecting from 1337 port" % (client.id, client.ip))
            self.console.queueEvent(b3.events.Event(b3.events.EVT_1337_PORT, data=None, client=client))
            client.notice("1337 port detected", None)
            self.tell_admins_except_one(client, '%s^7 (@%s) is probably hacking. (1337 port)' % (client.exactName, client.id))
            if self.port_1337_penalty and PENALTIES[self.port_1337_penalty] > PENALTIES[penalty]:
                penalty = self.port_1337_penalty

        client.setvar(self, 'haxBusted', busted)
        if busted:
            reasons_msg = ', '.join(reasons)
            if penalty == PENALTY_KICK:
                self.info('kicking client because of : %s' % reasons_msg)
                client.kick(reason='Not welcome on this server', keyword="haxbusterurt", silent=True, data=reasons_msg)
            elif penalty == PENALTY_TEMPBAN:
                self.info('tempban client because of : %s' % reasons_msg)
                client.tempban(duration=self.tempban_duration, reason='Not welcome on this server', keyword="haxbusterurt", silent=True, data=reasons_msg)
            elif penalty == PENALTY_PERMBAN:
                self.info('permban client because of : %s' % reasons_msg)
                client.ban(reason='Not welcome on this server', keyword="haxbusterurt", silent=True, data=reasons_msg)

        
    def isBadGuid(self, client):
        ## have we checked this client before ?
        cachedResult = client.var(self, 'haxBusted_bad_guid').value
        if cachedResult is not None:
            self.debug('%s was checked before : %s' % (client.name, cachedResult))
            return cachedResult

        ## empty guid client property o_O should not happen
        if client.guid is None:
            self.warning('That\'s weird, client @%s has no guid' % client.id)
            return False
        
        ## do not warn for AI bots
        if hasattr(client, 'ip') and client.ip == '0.0.0.0' and client.guid.startswith('BOT'):
            self.debug("AI bots aren't cheating")
            return False
        
        ## guid == ip --> reveals a clients that connects with an empty cl_guid
        if hasattr(client, 'ip') and client.ip == client.guid:
            self.info('player @%s (%s) has an empty guid' % (client.id, client.ip))
            client.setvar(self, 'haxBusted_bad_guid', not self.acceptEmptyGuid)
            return not self.acceptEmptyGuid
        
        # check normal ioUrbanTerror guid
        if self._reValidGuid.search(client.guid) is not None:
            client.setvar(self, 'haxBusted_bad_guid', False)
            self.info('%s is a valid ioUrT guid' % client.guid)
            return False
        else:
            self.info('%s is a not a valid ioUrT guid' % client.guid)
            client.setvar(self, 'haxBusted_bad_guid', True)
            return True


    def is_1337_port(self, client, clients_port=None):
        ## have we checked this client before ?
        cachedResult = client.var(self, 'haxBusted_1337_port').value
        if cachedResult is not None:
            self.debug('%s was checked before : %s' % (client.name, cachedResult))
            return cachedResult

        if clients_port is None or client.cid not in clients_port:
            clients_port = self.getPlayersPort()

        # cannot get client's port o.O
        if client.cid not in clients_port:
            self.warning("Could not find player port for %s" % client)
            return False

        ## do not warn for AI bots
        if hasattr(client, 'ip') and client.ip == '0.0.0.0' and client.guid.startswith('BOT'):
            self.debug("AI bots aren't cheating")
            return False

        # check port
        port = clients_port[client.cid]
        if port != '1337':
            client.setvar(self, 'haxBusted_1337_port', False)
            self.info('%s is not connecting from 1337 port : %s' % (client.cid, port))
            return False
        else:
            self.info('%s is connecting from 1337 port' % client.cid)
            client.setvar(self, 'haxBusted_1337_port', True)
            return True


    def tell_admins_except_one(self, excluded_client, msg):
        """send a private message to all on-line admins excepted excluded_client"""
        for c in self.console.clients.getClientsByLevel(min=self._adminLevel):
            if c == excluded_client:
                continue
            c.message(msg)



    def getPlayersPort(self):
        data = self.console.write('status')
        if not data:
            return {}

        players = {}
        for line in data.split('\n'):
            m = re.match(self.console._regPlayer, line.strip())
            if m:
                if m.group('port'):
                    players[m.group('slot')] = m.group('port')
        return players

