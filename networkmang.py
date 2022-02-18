'''
This module contains the classes to represent
wireless interfaces as well as methods to handle them
and their information
'''

import os
import pyric.pyw as pyw
from utils import NetUtils, FileHandler
from subprocess import check_output
from textwrap import dedent

class NetworkCard(object):

    def __init__(self, interface):

        self.interface = interface
        self.card = None
        self.modes = None
        self.original_mac = None
        self._ap_mode_support = None
        self._monitor_mode_support = None

        try:
            self.card = pyw.getcard(interface)
            self.modes = pyw.devmodes(self.card)
            self.original_mac = pyw.macget(self.card)

            # Important capabilities
            self._ap_mode_support = "AP" in self.modes
            self._monitor_mode_support = "monitor" in self.modes
        except: pass

        self._number_of_supported_aps = None
        self._is_managed = False

    def _valid_card(self):
        return self.card is not None

    def set_managed(self, state):
        self._is_managed = state

    def is_managed(self):
        return self._is_managed

    def set_txpower(self, dbm):
        if self._verify_card():
            pyw.txset(self.card, 'fixed', dbm)

    def get_txpower(self):
        if self._verify_card():
            return pyw.txget(self.card)

    def set_mode(self, mode):
        try:
            pyw.down(self.card)
            pyw.modeset(self.card, mode)
            pyw.up(self.card)
        except Exception as e:
            print e, "\n[-] Unable to set mode on {}".format(self.interface)
            return False

    def get_mode(self):
        try:
            return pyw.modeget(self.card)
        except Exception:
            return None

    def set_mac(self, mac):
        try:
            pyw.down(self.card)
            # If card was in monitor mode then macset wouldn't work right
            if pyw.modeget(self.card) == "monitor":
                pyw.modeset(self.card, "managed")
            pyw.macset(self.card, mac)
            pyw.up(self.card)
            return True
        except Exception as e:
            print e, "\n[-] Unable to set mac on {}".format(self.interface)
            return False

    def get_mac(self):
        try:
            return pyw.macget(self.card)
        except:
            return None

    def ifconfig(self, ip, netmask=None, broadcast=None):
        if self._valid_card():
            pyw.up(self.card)
            pyw.ifaddrset(self.card, ip, netmask, broadcast)

    def get_ip(self):
        try:
            return pyw.ifaddrget(self.card)[0]
        except:
            return None
