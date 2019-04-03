import inspect
import appdaemon.plugins.hass.hassapi as hass
import re


class BaseClass(hass.Hass):

    def _log(self, msg, prefix=None):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        callername = calframe[1][3]
        if prefix is not None and prefix != "":
            self.log("%s: %s: %s: %s" %
                     (self.__class__.__name__, prefix, callername, msg))
        else:
            self.log("%s: %s: %s" % (self.__class__.__name__, callername, msg))

    def _log_debug(self, msg, prefix=None):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        callername = calframe[1][3]
        if self.args["debug"]:
            if prefix is not None and prefix != "":
                self.log("DEBUG: %s: %s: %s: %s" %
                         (self.__class__.__name__, prefix, callername, msg))
            else:
                self.log("DEBUG: %s: %s: %s" %
                         (self.__class__.__name__, callername, msg))

    def _log_error(self, msg, prefix=None):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        callername = calframe[1][3]
        if prefix is not None and prefix != "":
            self.log("%s: %s: %s: %s" %
                     (self.__class__.__name__, prefix, callername, msg))
        else:
            self.log("%s: %s: %s" % (self.__class__.__name__, callername, msg))

    def _getattribute(self, statedict, entity, atr):
        return statedict.get(entity).get("attributes").get(atr, None)

    def _convertname(self, name):
        if name is not None and name != "":
            return name.lower().replace(" ", "_")
        else:
            return None

    def _getid(self, statedict, entity):
        idlist = ['friendly_name', 'id', 'value_id']
        count = 0
        id = None
        while id is None and count < len(idlist):
            self._log_debug("idlist: %s" % idlist[count])
            id = self._convertname(self._getattribute(
                statedict, entity, idlist[count]))
            count += 1
        if id is None:
            # id is still None. We have to clarify where to get the id
            self._log_debug("Could not detect id of the item. Values %s" %
                            self.statetict.get(entity))
        return id

    def _anyone_home(self, regex='^person.*'):
        statedict = self.get_state()
        anyonehome = False
        for entity in statedict:
            if re.match(regex, entity, re.IGNORECASE):
                id = self._getid(statedict, entity)
                state = self.get_state(entity)
                self._log_debug("Person %s is %s" % (id, state))
                if state == "home":
                    anyonehome = True
        return anyonehome
