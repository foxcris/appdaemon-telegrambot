from helper.Helper import BaseClass
import re
import hashlib
import ast
from datetime import datetime

class TelegramBot(BaseClass):

    def initialize(self):

        self._commanddict = {"/help": {"desc": "Help", "method": self._cmd_help},
                             "/state_cover": {"desc": "State of cover", "method": self._cmd_state_cover},
                             "/state_vacuum": {"desc": "State of vacuum", "method": self._cmd_state_vacuum},
                             "/state_light": {"desc": "State of light", "method": self._cmd_state_light},
                             "/state_climate": {"desc": "State of climate", "method": self._cmd_state_climate},
                             "/state_person": {"desc": "State of person", "method": self._cmd_state_person},
                             "/open_cover": {"desc": "Open cover", "method": self._cmd_open_cover},
                             "/close_cover": {"desc": "Close cover", "method": self._cmd_close_cover},
                             "/turnoff_light": {"desc": "Turn off light", "method": self._cmd_turn_off_light},
                             "/turnon_light": {"desc": "Turn on light", "method": self._cmd_turn_on_light},
                             "/start_vacuum": {"desc": "Start vacuum", "method": self._cmd_start_vacuum},
                             "/stop_vacuum": {"desc": "Stop running vacuum", "method": self._cmd_stop_vacuum},
                             "/restart_hass": {"desc": "Restart hass", "method": self._cmd_restart_hass},
                             "/state_system": {"desc": "State of home-assistant", "method": self._cmd_state_system},
                             "/state_sensor": {"desc": "State of sensors", "method": self._cmd_state_sensor},
                             "/get_version": {"desc": "Get version of telegrambot", "method": self._cmd_get_version},
                             "/turnon_automation": {"desc": "Turn on automation", "method": self._cmd_turn_on_automation},
                             "/turnoff_automation": {"desc": "Turn off automation", "method": self._cmd_turn_off_automation},
                             "/trigger_automation": {"desc": "Trigger automation", "method": self._cmd_trigger_automation},
                             "/state_automation": {"desc": "State of automation", "method": self._cmd_state_automation},
                             "/get_log": {"desc": "Get last lines of the home-assistant log", "method": self._cmd_get_log},
                             "/get_error_log": {"desc": "Get home-assistant error log", "method": self._cmd_get_error_log}}
        #[...]Data to be sent in a callback query to the bot when button is pressed, 1-64 bytes[...]
        #https://core.telegram.org/bots/api
        self._callbackdict = {"/clb_restart_hass": {"desc": "Restart hass", "method": self._clb_restart_hass},
                              "/clb_start_vacuum": {"desc": "Start vacuum", "method": self._clb_start_vacuum},
                              "/clb_stop_vacuum": {"desc": "Start vacuum", "method": self._clb_stop_vacuum},
                              "/clb_open_cover": {"desc": "Open cover", "method": self._clb_open_cover},
                              "/clb_close_cover": {"desc": "Close cover", "method": self._clb_close_cover},
                              "/clb_turnoff_light": {"desc": "Turn off light", "method": self._clb_turn_off_light},
                              "/clb_turnon_light": {"desc": "Turn on light", "method": self._clb_turn_on_light},
                              "/clb_turnoff_autom": {"desc": "Turn off automation", "method": self._clb_turn_off_autom},
                              "/clb_turnon_autom": {"desc": "Turn on automation", "method": self._clb_turn_on_autom},
                              "/clb_trigger_autom": {"desc": "Trigger automation", "method": self._clb_trigger_autom}}

        self.listen_event(self._receive_telegram_command, 'telegram_command')
        self.listen_event(self._receive_telegram_callback, 'telegram_callback')
        self.listen_event(self._receive_telegram_text, 'telegram_text')
        self.listen_state(
            self._homeassistant_update_available,
            "binary_sensor.updater", duration=1)
        self.listen_event(self._homeassistant_restarted, "homeassistant_start")
        self.listen_event(self._appdaemon_restarted, 'appd_started')
        self._entityid_hash_dict = dict()
        self._hash_entityid_dict = dict()
        self._version=1.2.1
        
        self._log_debug(self.args)

        #handle extend
        self._extend_system = list()
        if self.args["extend_system"] is not None and self.args["extend_system"]!="":
            self._extend_system=self.args["extend_system"].split(',')
        self._log_debug(f"extend_system: {self._extend_system}")

        self._extend_light = list()
        if self.args.get("extend_light",None) is not None and self.args.get("extend_light")!="":
            self._extend_light=self.args["extend_light"].split(',')
        self._log_debug(f"extend_light: {self._extend_light}")

        self._filter_blacklist = None
        if self.args.get("filter_blacklist", None) is not None and self.args.get("filter_blacklist")!="":
            self._filter_blacklist=self.args.get("filter_blacklist")
        self._log_debug(f"filter_blacklist: {self._filter_blacklist}")
        
        self._filter_whitelist = None
        if self.args.get("filter_whitelist", None) is not None and self.args.get("filter_whitelist")!="":
            self._filter_whitelist=self.args.get("filter_whitelist")
        self._log_debug(f"filter_whitelist: {self._filter_whitelist}")

        self._routing = self.args.get("routing", None)
        self._log_debug(f"routing: {self._routing}")

        self._hass = self.args.get("hass", None)
        self._log_debug(f"hass: {self._hass}")


    def _receive_telegram_command(self, event_id, payload_event, *args):
        user_id = payload_event['user_id']
        chat_id = payload_event['chat_id']
        command = payload_event['command'].lower()

        self._log_debug(f"Telegram Command: user_id: {user_id}, chat_id: {chat_id}, command: {command}")
        self._log_debug(f"Paylod_event: {payload_event}")

        if command in self._commanddict:
            method = self._commanddict.get(command).get('method')
            method(user_id)
        else:
            msg = f"Unkown command {command}. Use /help to get a list of all available commands."
            self.call_service(
                'telegram_bot/send_message',
                target=user_id,
                message=self._escape_markdown(msg))
    
    def _receive_telegram_text(self, event_id, payload_event, *args):
        user_id = payload_event['user_id']
        chat_id = payload_event['chat_id']
        text = ast.literal_eval(payload_event.get('text'))

        self._log_debug(f"Telegram Command: user_id: {user_id}, chat_id: {chat_id}, text: {text}")
        self._log_debug(f"Paylod_event: {payload_event}")

        #check if location was sent
        if isinstance(text, dict) and text.get('location',None) is not None:
            location = text.get('location',dict())
            longitude = location.get('longitude',None)
            latitude = location.get('latitude',None)
            self._compute_travel_time(user_id, longitude, latitude)

    def _escape_markdown(self, msg):
        msg = msg.replace("`", "\\`")
        msg = msg.replace("*", "\\*")
        msg = msg.replace("_", "\\_")

        return msg

    def _cmd_help(self, target_id):
        msg = "The following commands are available:\n/help: This help\n"
        keyboard_options=list()
        for command in self._commanddict:
            desc = self._commanddict.get(command).get("desc")
            msg += f"{command} : {desc}\n"
            button=command.replace("/","").replace("_"," ")
            keyboard_options.append({
                'description': desc, 
                'url': command,
                'button': button})
        self._log_debug(msg)
        self._build_keyboard_answer(keyboard_options, target_id, keyboard_width=2)

    def _cmd_state_cover(self, target_id):
        statedict = self._get_state_filtered()
        msg = ""
        for entity in statedict:
            if re.match('^cover.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                state = statedict.get(entity).get("state")
                desc = self._getid(statedict, entity)
                current_position = statedict.get(entity).get(
                    "attributes").get("current_position")

                msg += f"{desc}\nstate: {state}\ncurrent_position: {current_position}\n\n"
        self._log_debug(msg)
        self._send_message(msg, target_id)

    def _cmd_state_person(self, target_id):
        statedict = self._get_state_filtered()
        for entity in statedict:
            if re.match('^person.*', entity, re.IGNORECASE):
                self._log_debug(f"Person: {entity}")
                self._log_debug(f"statedict: {statedict.get(entity)}")
                state = statedict.get(entity).get("state")
                desc = self._getid(statedict,entity)
                latitude = statedict.get(entity).get(
                    "attributes").get("latitude")
                longitude = statedict.get(entity).get(
                    "attributes").get("longitude")
                gps_accuracy = statedict.get(entity).get(
                    "attributes").get("gps_accuracy")

                msg = f"{desc}\nstate: {state}\nlatitude: {latitude}\nlongitude: {longitude}\ngps_accuracy: {gps_accuracy}\n\n"
                self._log_debug(f"msg person: {msg}")
                self._send_message(msg, target_id)
                self.call_service(
                    'telegram_bot/send_location',
                    target=target_id,
                    latitude=latitude,
                    longitude=longitude)

    def _cmd_state_vacuum(self, target_id):
        statedict = self._get_state_filtered()
        msg = ""
        for entity in statedict:
            if re.match('^vacuum.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                state = statedict.get(entity).get("state")
                desc = self._getid(statedict,entity)
                battery_level = statedict.get(entity).get(
                    "attributes").get("battery_level")

                msg += f"{desc}\nstate: {state}\nbattery_level: {battery_level}\n\n"
        self._log_debug(msg)
        self._send_message(msg, target_id)

    def _cmd_state_light(self, target_id):
        statedict = self._get_state_filtered()
        msg=""
        for entity in statedict:
            if re.match('^light.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                state = statedict.get(entity).get("state")
                desc = self._getid(statedict,entity)
                msg += f"{desc}\nstate: {state}\n\n"
                
        for entity in self._extend_light:
            l = entity.strip()
            self._log_debug(l)
            state = self.get_state(l)
            desc = self._getid(statedict, l)
            msg += f"{desc}\nstate: {state}\n\n"

        self._log_debug(msg)
        self._send_message(msg, target_id)

    def _cmd_state_climate(self, target_id):
        statedict = self._get_state_filtered()
        msg = ""
        for entity in statedict:
            if re.match('^climate.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                state = statedict.get(entity).get("state")
                current_temperature = statedict.get(entity).get(
                    "attributes").get("current_temperature")
                temperature = statedict.get(entity).get(
                    "attributes").get("temperature")
                desc = self._getid(statedict,entity)
                msg += f"{desc}\nstate: {state}\ncurrent temperature: {current_temperature}\ntemperature: {temperature}.\n\n"

        self._send_message(msg, target_id)

    def _clb_open_cover(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if hashvalue == "all":
            self.call_service("cover/open_cover", entity_id="all")
            msg = "Open all covers!"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
        elif entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Open cover {entity_id} ({friendly_name})"
            self.call_service("cover/open_cover",
                            entity_id=entity_id)
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self._send_message(msg, target_id)

    def _cmd_open_cover(self, target_id):
        msg = "Which cover do you want to open?\n\n"
        statedict = self._get_state_filtered()
        keyboard_options=list()
        keyboard_options.append({
                    'description': f"Open all covers", 
                    'url':f"/clb_open_cover?entity_id=all"})
        for entity in statedict:
            if re.match('^cover.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                hashvalue = self._get_hash_from_entityid(entity)
                desc = self._getid(statedict,entity)
                keyboard_options.append({
                    'description': f"{desc}", 
                    'url':f"/clb_open_cover?entity_id={hashvalue}"})
        
        self._build_keyboard_answer(keyboard_options, target_id, msg)

    def _cmd_close_cover(self, target_id):
        msg = "Which cover do you want to close?\n\n"
        statedict = self._get_state_filtered()
        keyboard_options=list()
        keyboard_options.append({
                    'description': f"Close all covers", 
                    'url':f"/clb_close_cover?entity_id=all"})
        for entity in statedict:
            if re.match('^cover.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                hashvalue = self._get_hash_from_entityid(entity)
                desc = self._getid(statedict,entity)
                keyboard_options.append({
                    'description': f"{desc}", 
                    'url':f"/clb_close_cover?entity_id={hashvalue}"})
        
        self._build_keyboard_answer(keyboard_options, target_id, msg)

    def _clb_close_cover(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if hashvalue == "all":
            self.call_service("cover/close_cover", entity_id="all")
            msg = "Close all covers!"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
        elif entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Close cover {entity_id} ({friendly_name})"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self.call_service("cover/close_cover",
                              entity_id=entity_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self._send_message(msg, target_id)

    def _cmd_turn_off_light(self, target_id):
        msg = "Which light do you want to turn off?\n\n"
        statedict = self._get_state_filtered()
        keyboard_options=list()
        keyboard_options.append({
                    'description': f"Turn off all lights", 
                    'url':f"/clb_turnoff_light?entity_id=all"})
        for entity in statedict:
            if re.match('^light.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                hashvalue = self._get_hash_from_entityid(entity)
                desc = self._getid(statedict,entity)
                keyboard_options.append({
                    'description': f"{desc}", 
                    'url':f"/clb_turnoff_light?entity_id={hashvalue}"})
        
        for entity in self._extend_light:
            self._log_debug(statedict.get(entity))
            hashvalue = self._get_hash_from_entityid(entity)
            desc = self._getid(statedict,entity)
            keyboard_options.append({
                'description': f"{desc}", 
                'url':f"/clb_turnoff_light?entity_id={hashvalue}"})
        
        self._build_keyboard_answer(keyboard_options, target_id, msg,)

    def _clb_turn_off_light(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if hashvalue == "all":
            self.call_service("light/turn_off", entity_id="all")
            msg = "Turn off all lights!"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
        elif entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Turn off light {entity_id} ({friendly_name})"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self._turn_off(entity_id)

        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self._send_message(msg, target_id)

    def _cmd_turn_on_light(self, target_id):
        msg = "Which light do you want to turn on?\n\n"
        statedict = self._get_state_filtered()
        keyboard_options=list()
        keyboard_options.append({
                    'description': f"Turn on all lights", 
                    'url':f"/clb_turnon_light?entity_id=all"})
        for entity in statedict:
            if re.match('^light.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                hashvalue = self._get_hash_from_entityid(entity)
                desc = self._getid(statedict,entity)
                keyboard_options.append({
                    'description': f"{desc}", 
                    'url':f"/clb_turnon_light?entity_id={hashvalue}"})
                    
        for entity in self._extend_light:
            self._log_debug(statedict.get(entity))
            hashvalue = self._get_hash_from_entityid(entity)
            desc = self._getid(statedict,entity)
            keyboard_options.append({
                'description': f"{desc}", 
                'url':f"/clb_turnon_light?entity_id={hashvalue}"})
        
        self._build_keyboard_answer(keyboard_options, target_id, msg)

    def _clb_turn_on_light(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if hashvalue == "all":
            self.call_service("light/turn_on", entity_id="all")
            msg = "Turn on all lights!"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
        elif entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Turn on light {entity_id} ({friendly_name})"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self._turn_on(entity_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id,
                show_alert=True)

    def _cmd_restart_hass(self, target_id):
        msg = "Restart home-assistant?"
        keyboard = [[("Yes", "/clb_restart_hass?value=yes"), ("No",
                                                          "/clb_restart_hass?value=no")]]
        self._send_message_with_inline_keyboard(msg, target_id, keyboard)

    def _cmd_start_vacuum(self, target_id):
        msg = "Which vacuum do you want to start?\n\n"
        statedict = self._get_state_filtered()
        keyboard_options=list()
        for entity in statedict:
            if re.match('^vacuum.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                hashvalue = self._get_hash_from_entityid(entity)
                desc = self._getid(statedict,entity)
                state = statedict.get(entity).get("state")
                battery_level = statedict.get(entity).get(
                        "attributes").get("battery_level")
                keyboard_options.append({
                    'description': f"{desc}\nstate: {state}\nbattery_level: {battery_level}", 
                    'url':f"/clb_start_vacuum?entity_id={hashvalue}"})
        
        self._build_keyboard_answer(keyboard_options, target_id, msg)

    def _clb_start_vacuum(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Starting vacuum {entity_id} ({friendly_name})"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self.call_service("vacuum/start",
                              entity_id=entity_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id,
                show_alert=True)

    def _cmd_stop_vacuum(self, target_id):
        msg = "Which vacuum do you want to stop?\n\n"
        statedict = self._get_state_filtered()
        keyboard_options=list()
        for entity in statedict:
            if re.match('^vacuum.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                hashvalue = self._get_hash_from_entityid(entity)
                desc = self._getid(statedict,entity)
                state = statedict.get(entity).get("state")
                battery_level = statedict.get(entity).get(
                        "attributes").get("battery_level")
                keyboard_options.append({
                    'description': f"{desc}\nstate: {state}\nbattery_level: {battery_level}", 
                    'url':f"/clb_stop_vacuum?entity_id={hashvalue}"})

        self._build_keyboard_answer(keyboard_options, target_id, msg)

    def _clb_stop_vacuum(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Stopping vacuum {entity_id} ({friendly_name})"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self.call_service("vacuum/return_to_base",
                              entity_id=entity_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self._send_message(msg, target_id)

    def _receive_telegram_callback(self, event_id, payload_event, *args):
        data_callback = payload_event['data'].lower()
        callback_id = payload_event['id']

        self._log_debug(f"Telegram Callback: data_callback: {data_callback}, callback_id: {callback_id}")
        self._log_debug(f"Paylod_event: {payload_event}")

        if "?" in data_callback:
            callback, params = data_callback.split("?")
        else:
            callback = data_callback
            params = None
        if params is not None:
            params = dict(item.split("=") for item in params.split(";"))
        if callback in self._callbackdict:
            method = self._callbackdict.get(callback).get('method')
            method(target_id=callback_id, paramdict=params)
        if callback in self._commanddict:
            method = self._commanddict.get(callback).get('method')
            method(target_id=callback_id)
            #https://python-telegram-bot.readthedocs.io/en/stable/telegram.callbackquery.html
            #After the user presses an inline button, Telegram clients will display a progress 
            #bar until you call answer. It is, therefore, necessary to react by calling 
            #telegram.Bot.answer_callback_query even if no notification to the user is needed 
            #(e.g., without specifying any of the optional parameters).
            self.call_service(
                'telegram_bot/answer_callback_query',
                message="",
                callback_query_id=callback_id)

    def _clb_restart_hass(self, target_id, paramdict):
        if paramdict.get("value") and paramdict.get("value").lower() == "yes":
            msg = "Restarting home-assistant!"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id,
                show_alert=True)
            self.call_service(
                'homeassistant/restart')
        elif paramdict.get("value") and paramdict.get("value").lower() == "no":
            msg = "Ok. Not restarting home-assistant!"
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self._send_message(msg, target_id)
        else:
            msg = "Missing value!"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message="",
                callback_query_id=target_id)

    def _get_hash_from_entityid(self, entity_id):
        h = self._entityid_hash_dict.get(entity_id,None) 
        if h is None:
            h = hashlib.md5(entity_id.encode('utf-8')).hexdigest()
            self._entityid_hash_dict.update({entity_id: h})
            self._hash_entityid_dict.update({h: entity_id})
        return h

    def _get_entityid_from_hash(self, hashvalue):
        h = self._hash_entityid_dict.get(hashvalue,None)
        return h

    def _homeassistant_update_available(self, entity, attribute, old, new, duration):
        if new == "on":
            newest_version = self.get_state(entity, attribute="newest_version")
            release_notes = self.get_state(entity, attribute="release_notes")
            msg = f"Home-assistant update available! Newest version: {newest_version}.\n Release Notes: {release_notes}"
            self._log_info(msg)
            self.call_service(
                'telegram_bot/send_message',
                message=self._escape_markdown(msg))

    def _homeassistant_restarted(self, event_id, payload_event, *args):
        msg = f"Home-assistant restarted!"
        self._log_info(msg)
        self.call_service(
            'telegram_bot/send_message',
            message=self._escape_markdown(msg))

    def _appdaemon_restarted(self, event_id, payload_event, *args):
        msg = f"Appdaemon restarted!"
        self._log_info(msg)
        self.call_service(
            'telegram_bot/send_message',
            message=self._escape_markdown(msg))

    def _cmd_state_system(self, target_id):
        #to report the system state we are using the systemonitor integration
        #https://www.home-assistant.io/integrations/systemmonitor/

        sensorlist = [ 'disk_use_percent',
                        'disk_use',
                        'disk_free',
                        'memory_use_percent'
                        'memory_use',
                        'memory_free',
                        'swap_use_percent',
                        'swap_use',
                        'swap_free',
                        'load_1m',
                        'load_5m',
                        'load_15m',
                        'network_in',
                        'network_out',
                        'throughput_network_in',
                        'throughput_network_out',
                        'packets_in',
                        'packets_out',
                        'ipv4_address',
                        'ipv6_address',
                        'processor_use',
                        'process',
                        'last_boot']
        msg = ""
        
        statedict = self._get_state_filtered()
        for entity in statedict:
            if re.match(f"^sensor.({'|'.join(sensorlist)}).*", entity, re.IGNORECASE):
                state = self.get_state(entity)
                desc = self._getid(statedict,entity)
                unit_of_measurement=self.get_state(entity, attribute='unit_of_measurement')
                if state is not None:
                    msg+=f"{desc}: {state}{unit_of_measurement}\n"
        
        for sensor in self._extend_system:
            s = sensor.strip()
            self._log_debug(s)
            state = self.get_state(s)
            desc = self._getid(statedict, s)
            unit_of_measurement=self.get_state(s, attribute='unit_of_measurement')
            if unit_of_measurement is None:
                unit_of_measurement=""
            if state is not None:
                msg+=f"{desc}: {state}{unit_of_measurement}\n"

        self._log_debug(msg)
        self._send_message(msg, target_id)
            
    def _cmd_get_version(self, target_id):
        msg = f"TelegramBot Version: {self._version}"
        self._send_message(msg, target_id)

    def _build_keyboard_answer(self, items, target_id, msgprefix=None, msgsuffix=None, keyboard_width=8):
        """ items: list of dictionaries in the form [{'description':'', 'url':'', 'botton': ''}]
        """
        keyboard = list()
        keyboardrow = list()
        count = 1
        msg = ""
        if msgprefix is not None:
            msg = msgprefix

        for item in items:
            button = item.get('button',count)
            url = item.get('url',"/help")
            desc = item.get('description',"")
            keyboardrow.append((button, url))
            msg += f"{button}: {desc}\n"
            count+=1
            if count % keyboard_width == 0:
                keyboard.append(keyboardrow)
                keyboardrow = list()
        
        if len(keyboardrow) > 0:
            keyboard.append(keyboardrow)
        
        self._log_debug(msg)
        self._log_debug(keyboard)
        if msgsuffix is not None:
            msg+=msgsuffix
        self._send_message_with_inline_keyboard(msg, target_id, keyboard)

    def _cmd_state_sensor(self, target_id):
        statedict = self._get_state_filtered()
        msg = ""
        for entity in statedict:
            if re.match('^sensor.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                state = statedict.get(entity).get("state")
                desc = self._getid(statedict,entity)
                msg += f"{desc}\nstate: {state}\n\n"

        self._log_debug(msg)
        self._log_debug(f"Len: {len(msg)}")
        self._send_message(msg, target_id)

    def _send_message(self, msg, target_id):
        #https://python-telegram-bot.readthedocs.io/en/stable/telegram.constants.html?highlight=max%20length#telegram.constants.MAX_MESSAGE_LENGTH
        while len(msg)>4096:
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg[:4096]))
            msg=msg[4096:]
        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg[:4096]))

    def _send_message_with_inline_keyboard(self, msg, target_id, keyboard):
        while len(msg)>4096:
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg[:4096]))
            msg=msg[4096:]
        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg),
            inline_keyboard=keyboard)
        
    def _get_state_filtered(self):
        statedict = self.get_state()
        filtered_statedict=dict()
        for entity in statedict:
            #filter by blacklist
            blacklisted=True
            if self._filter_blacklist is not None:              
                prepare="|".join(self._filter_blacklist)
                blacklistregex=f"({prepare})"
            else:
                blacklistregex=""   
            
            #filter by whitelist
            whitelisted=True    
            if self._filter_whitelist is not None:
                prepare="|".join(self._filter_whitelist)
                whitelistregex=f"({prepare})"
            else:
                whitelistregex=".*"
            
            #apply filter
            if not re.search(blacklistregex, entity, re.IGNORECASE) and re.search(whitelistregex, entity, re.IGNORECASE):
                filtered_statedict.update({entity: statedict.get(entity)})
            
        return filtered_statedict

    def _cmd_turn_on_automation(self, target_id):
        msg = "Which automation do you want to turn on?\n\n"
        statedict = self._get_state_filtered()
        keyboard_options=list()
        for entity in statedict:
            if re.match('^automation.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                hashvalue = self._get_hash_from_entityid(entity)
                desc = self._getid(statedict,entity)
                keyboard_options.append({
                    'description': f"{desc}", 
                    'url':f"/clb_turnon_autom?entity_id={hashvalue}"})
        
        self._build_keyboard_answer(keyboard_options, target_id, msg)

    def _clb_turn_on_autom(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Turn on automation {entity_id} ({friendly_name})"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self._turn_on(entity_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id,
                show_alert=True)

    def _cmd_turn_off_automation(self, target_id):
        msg = "Which automation do you want to turn off?\n\n"
        statedict = self._get_state_filtered()
        keyboard_options=list()
        for entity in statedict:
            if re.match('^automation.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                hashvalue = self._get_hash_from_entityid(entity)
                desc = self._getid(statedict,entity)
                keyboard_options.append({
                    'description': f"{desc}", 
                    'url':f"/clb_turnoff_autom?entity_id={hashvalue}"})
        
        self._build_keyboard_answer(keyboard_options, target_id, msg)

    def _clb_turn_off_autom(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Turn off automation {entity_id} ({friendly_name})"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self._turn_off(entity_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id,
                show_alert=True)

    def _cmd_trigger_automation(self, target_id):
        msg = "Which automation do you want to trigger?\n\n"
        statedict = self._get_state_filtered()
        keyboard_options=list()
        for entity in statedict:
            if re.match('^automation.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                hashvalue = self._get_hash_from_entityid(entity)
                desc = self._getid(statedict,entity)
                keyboard_options.append({
                    'description': f"{desc}", 
                    'url':f"/clb_trigger_autom?entity_id={hashvalue}"})
        
        self._build_keyboard_answer(keyboard_options, target_id, msg)

    def _clb_trigger_autom(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Trigger automation {entity_id} ({friendly_name})"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self.call_service("automation/trigger",
                              entity_id=entity_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self._send_message(msg, target_id)
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id,
                show_alert=True)

    def _cmd_state_automation(self, target_id):
        statedict = self._get_state_filtered()
        msg = ""
        for entity in statedict:
            if re.match('^automation.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                state = statedict.get(entity).get("state")
                desc = self._getid(statedict, entity)
                last_triggered = statedict.get(entity).get(
                    "attributes").get("last_triggered")

                msg += f"{desc}\nstate: {state}\nlast_triggered: {last_triggered}\n\n"
        self._log_debug(msg)
        self._send_message(msg, target_id)

    def _compute_travel_time(self, user_id, longitude, latitude):
        WazeRouteCalculator = self.import_install_module('WazeRouteCalculator')
        region = 'EU'
        avoid_toll_roads = False
        if self._routing is not None:
            #check which backend is configured
            #here = self._routing.get('here',None)
            waze = self._routing.get('waze',None)
            if waze is not None:
                region = waze.get('region', 'EU')
                avoid_toll_roads = waze.get('avoid_toll_roads', False)

        statedict = self.get_state()
        for entity in statedict:
            if re.match('^zone.*', entity, re.IGNORECASE):
                zone = statedict.get(entity)
                self._log_debug(zone)
                zone_latitude=self.get_state(entity, attribute='latitude')
                zone_longitude=self.get_state(entity, attribute='longitude')
                desc=self._getid(statedict, entity)
                retry=0
                maxretry=5
                while retry<maxretry:
                    try:
                        wazeroute = WazeRouteCalculator.WazeRouteCalculator(f"{latitude},{longitude}", f"{zone_latitude},{zone_longitude}", region, avoid_toll_roads)
                        route_time, route_distance = wazeroute.calc_route_info()
                        msg = f"Route to '{desc}'\nRequired Time: {route_time:.2f} minutes\nDistance: {route_distance:.2f} km"
                        self._log_debug(msg)
                        self._send_message(msg, user_id)
                        retry=maxretry
                    except Exception as e:
                        self._log_error(e)
                        retry+=1
                        if retry==maxretry:
                            self._log_error(f"Compute route to {desc} failed. Max retry reached.")
                        else:
                            self._log_error(f"Compute route to {desc} failed. Retry {retry} of {maxretry}.")

    def _cmd_get_log(self, target_id):
        #curl -X GET -H "Authorization: Bearer ABCDEFGH" \
        #-H "Content-Type: application/json" \
        #http://localhost:8123/api/error_log
        if self._hass is not None:
            token = self._hass.get('token', None)
            ha_url = self._hass.get('ha_url', None)
            if token is not None and ha_url is not None:
                requests = self.import_install_module('requests')
                custom_headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                res=requests.get(f"{ha_url}/api/error_log", headers=custom_headers)
                loglist=res.text.split('\n')
                lastlogs=loglist[-50:]
                self._send_message('\n'.join(lastlogs), target_id)

    def _cmd_get_error_log(self, target_id):
        #curl -X GET -H "Authorization: Bearer ABCDEFGH" \
        #-H "Content-Type: application/json" \
        #http://localhost:8123/api/error_log
        if self._hass is not None:
            token = self._hass.get('token', None)
            ha_url = self._hass.get('ha_url', None)
            if token is not None and ha_url is not None:
                requests = self.import_install_module('requests')
                custom_headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                res=requests.get(f"{ha_url}/api/error/all", headers=custom_headers)
                msg = ''
                for entry in res.json():
                    timestamp = entry.get('timestamp',None)
                    if timestamp is not None:
                        timestamp = datetime.fromtimestamp(timestamp)
                    errorlevel = entry.get('level',None)
                    message = entry.get('message',None)
                    msg += f"{timestamp} {errorlevel} {message}\n"
                self._send_message(msg, target_id)
                
    def _turn_on(self, entity_id):
        if re.match('^light.*', entity_id, re.IGNORECASE):
            self.call_service("light/turn_on", entity_id=entity_id)
        elif re.match('^automation.*', entity_id, re.IGNORECASE):
            self.call_service("automation/turn_on", entity_id=entity_id)
        elif re.match('^climate.*', entity_id, re.IGNORECASE):
            self.call_service("climate/turn_on", entity_id=entity_id)
        elif re.match('^fan.*', entity_id, re.IGNORECASE):
            self.call_service("fan/turn_on", entity_id=entity_id)
        elif re.match('^input_boolean.*', entity_id, re.IGNORECASE):
            self.call_service("input_boolean/turn_on", entity_id=entity_id)
        elif re.match('^media_player.*', entity_id, re.IGNORECASE):
            self.call_service("media_player/turn_on", entity_id=entity_id)
        elif re.match('^scene.*', entity_id, re.IGNORECASE):
            self.call_service("scene/turn_on", entity_id=entity_id)
        elif re.match('^script.*', entity_id, re.IGNORECASE):
            self.call_service("script/turn_on", entity_id=entity_id)
        elif re.match('^switch.*', entity_id, re.IGNORECASE):
            self.call_service("switch/turn_on", entity_id=entity_id)
        elif re.match('^vacuum.*', entity_id, re.IGNORECASE):
            self.call_service("vacuum/turn_on", entity_id=entity_id)
        else:
            self._log_error("Unsupported entity type for command turn_on")
        
    def _turn_off(self, entity_id):
        if re.match('^light.*', entity_id, re.IGNORECASE):
            self.call_service("light/turn_off", entity_id=entity_id)
        elif re.match('^automation.*', entity_id, re.IGNORECASE):
            self.call_service("automation/turn_off", entity_id=entity_id)
        elif re.match('^climate.*', entity_id, re.IGNORECASE):
            self.call_service("climate/turn_off", entity_id=entity_id)
        elif re.match('^fan.*', entity_id, re.IGNORECASE):
            self.call_service("fan/turn_off", entity_id=entity_id)
        elif re.match('^input_boolean.*', entity_id, re.IGNORECASE):
            self.call_service("input_boolean/turn_off", entity_id=entity_id)
        elif re.match('^media_player.*', entity_id, re.IGNORECASE):
            self.call_service("media_player/turn_off", entity_id=entity_id)
        elif re.match('^scene.*', entity_id, re.IGNORECASE):
            self.call_service("scene/turn_off", entity_id=entity_id)
        elif re.match('^script.*', entity_id, re.IGNORECASE):
            self.call_service("script/turn_off", entity_id=entity_id)
        elif re.match('^switch.*', entity_id, re.IGNORECASE):
            self.call_service("switch/turn_off", entity_id=entity_id)
        elif re.match('^vacuum.*', entity_id, re.IGNORECASE):
            self.call_service("vacuum/turn_off", entity_id=entity_id)
        else:
            self._log_error("Unsupported entity type for command turn_off")