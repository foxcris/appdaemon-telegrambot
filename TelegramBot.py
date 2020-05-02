from Helper import BaseClass
import re
import hashlib

class TelegramBot(BaseClass):

    def initialize(self):
        self._commanddict = {"/state_cover": {"desc": "State of cover", "method": self._cmd_state_cover},
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
                             "/state_system": {"desc": "State of home-assistant", "method": self._cmd_state_system}}
        self._callbackdict = {"/restart_hass": {"desc": "Restart hass", "method": self._clb_restart_hass},
                              "/start_vacuum": {"desc": "Start vacuum", "method": self._clb_start_vacuum},
                              "/stop_vacuum": {"desc": "Start vacuum", "method": self._clb_stop_vacuum},
                              "/open_cover": {"desc": "Open cover", "method": self._clb_open_cover},
                              "/close_cover": {"desc": "Close cover", "method": self._clb_close_cover},
                              "/turnoff_light": {"desc": "Turn off light", "method": self._clb_turn_off_light},
                              "/turnon_light": {"desc": "Turn on light", "method": self._clb_turn_on_light}}

        self.listen_event(self._receive_telegram_command, 'telegram_command')
        self.listen_event(self._receive_telegram_callback, 'telegram_callback')
        self.listen_state(
            self._homeassistant_update_available,
            "binary_sensor.updater", duration=1)
        self.listen_event(self._homeassistant_restarted, "homeassistant_start")
        self.listen_event(self._appdaemon_restarted, 'appd_started')
        self._entityid_hash_dict = dict()
        self._hash_entityid_dict = dict()
        self._extend_state_system = None
        if self.args["extend_state_system"] is not None and self.args["extend_state_system"]!="":
            self._extend_state_system=self.args["extend_state_system"].split(',')
        self._filter_state_system = None
        if self.args["filter_state_system"] is not None and self.args["filter_state_system"]!="":
            self._filter_state_system=self.args["filter_state_system"]

    def _receive_telegram_command(self, event_id, payload_event, *args):
        user_id = payload_event['user_id']
        chat_id = payload_event['chat_id']
        command = payload_event['command'].lower()

        self._log_debug(f"Telegram Command: user_id: {user_id}, chat_id: {chat_id}, command: {command}")
        self._log_debug(f"Paylod_event: {payload_event}")

        if command == "/help":
            msg = "The following commands are available:\n/help: This help\n"
            for command in self._commanddict:
                desc = self._commanddict.get(command).get("desc")
                msg += f"{command} : {desc}\n"
            self._log_debug(msg)
            self.call_service(
                'telegram_bot/send_message',
                target=user_id,
                message=self._escape_markdown(msg))
        elif command in self._commanddict:
            method = self._commanddict.get(command).get('method')
            method(user_id)
        else:
            msg = f"Unkown command {command}. Use /help to get a list of all available commands."
            self.call_service(
                'telegram_bot/send_message',
                target=user_id,
                message=self._escape_markdown(msg))

    def _escape_markdown(self, msg):
        msg = msg.replace("`", "\\`")
        msg = msg.replace("*", "\\*")
        msg = msg.replace("_", "\\_")
        return msg

    def _cmd_state_cover(self, target_id):
        statedict = self.get_state()
        msg = ""
        for entity in statedict:
            if re.match('^cover.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                entity_id = statedict.get(entity).get("entity_id")
                state = statedict.get(entity).get("state")
                friendly_name = statedict.get(entity).get(
                    "attributes").get("friendly_name")
                current_position = statedict.get(entity).get(
                    "attributes").get("current_position")

                msg += f"{entity_id} {friendly_name}\nstate: {state}\ncurrent_position: {current_position}\n\n"
        self._log_debug(msg)
        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg))

    def _cmd_state_person(self, target_id):
        statedict = self.get_state()
        for entity in statedict:
            if re.match('^person.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                entity_id = statedict.get(entity).get("entity_id")
                state = statedict.get(entity).get("state")
                friendly_name = statedict.get(entity).get(
                    "attributes").get("friendly_name")
                latitude = statedict.get(entity).get(
                    "attributes").get("latitude")
                longitude = statedict.get(entity).get(
                    "attributes").get("longitude")
                gps_accuracy = statedict.get(entity).get(
                    "attributes").get("gps_accuracy")

                msg = f"{entity_id} {friendly_name}\nstate: {state}\nlatitude: {latitude}\nlongitude: {longitude}\ngps_accuracy: {gps_accuracy}\n\n"
                self._log_debug(msg)
                self.call_service(
                    'telegram_bot/send_message',
                    target=target_id,
                    message=self._escape_markdown(msg))
                self.call_service(
                    'telegram_bot/send_location',
                    target=target_id,
                    latitude=latitude,
                    longitude=longitude)

    def _cmd_state_vacuum(self, target_id):
        statedict = self.get_state()
        msg = ""
        for entity in statedict:
            if re.match('^vacuum.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                entity_id = statedict.get(entity).get("entity_id")
                state = statedict.get(entity).get("state")
                friendly_name = statedict.get(entity).get(
                    "attributes").get("friendly_name")
                battery_level = statedict.get(entity).get(
                    "attributes").get("battery_level")

                msg += f"{entity_id} {friendly_name}\nstate: {state}\nbattery_level: {battery_level}\n\n"
        self._log_debug(msg)
        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg))

    def _cmd_state_light(self, target_id):
        statedict = self.get_state()
        msg = ""
        for entity in statedict:
            if re.match('^light.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                entity_id = statedict.get(entity).get("entity_id")
                state = statedict.get(entity).get("state")
                friendly_name = statedict.get(entity).get(
                    "attributes").get("friendly_name")

                msg += f"{entity_id} {friendly_name}\nstate: {state}\n\n"
        self._log_debug(msg)
        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg))

    def _cmd_state_climate(self, target_id):
        statedict = self.get_state()
        msg = ""
        for entity in statedict:
            if re.match('^climate.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                entity_id = statedict.get(entity).get("entity_id")
                state = statedict.get(entity).get("state")
                current_temperature = statedict.get(entity).get(
                    "attributes").get("current_temperature")
                temperature = statedict.get(entity).get(
                    "attributes").get("temperature")
                friendly_name = statedict.get(entity).get(
                    "attributes").get("friendly_name")

                msg += f"{entity_id} {friendly_name}\nstate: {state}\ncurrent temperature: {current_temperature}\ntemperature: {temperature}.\n\n"
        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg))

    def _clb_open_cover(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if hashvalue == "all":
            self.call_service("cover/open_cover", entity_id="all")
            msg = "Open all covers!"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
        elif entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Open cover {entity_id} ({friendly_name})"
            self.call_service("cover/open_cover",
                            entity_id=entity_id)
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))

    def _cmd_open_cover(self, target_id):
        msg = "Which cover do you want to open?\n"
        statedict = self.get_state()
        keyboard = list()
        keyboardrow = list()
        count = 1
        keyboardrow.append(
            (count, f"/open_cover?entity_id=all"))
        msg += f"{count}: Open all covers)\n\n"
        count += 1
        for entity in statedict:
            if re.match('^cover.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                entity_id = statedict.get(entity).get("entity_id")
                hashvalue = self._get_hash_from_entityid(entity_id)
                friendly_name = statedict.get(entity).get(
                    "attributes").get("friendly_name")
                keyboardrow.append(
                    (count, f"/open_cover?entity_id={hashvalue}"))
                msg += f"{count}: {entity_id} ({friendly_name})\n\n"
                count += 1
                # start a new row after 8 buttons
                # only 8 buttins can be shown in one line (atleast on my phone)
                if count % 8 == 0:
                    keyboard.append(keyboardrow)
                    keyboardrow = list()

        if len(keyboardrow) > 0:
            keyboard.append(keyboardrow)

        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg),
            inline_keyboard=keyboard)

    def _cmd_close_cover(self, target_id):
        msg = "Which cover do you want to close?\n"
        statedict = self.get_state()
        keyboard = list()
        keyboardrow = list()
        count = 1
        keyboardrow.append(
            (count, f"/close_cover?entity_id=all"))
        msg += f"{count}: Close all covers)\n\n"
        count += 1
        for entity in statedict:
            if re.match('^cover.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                entity_id = statedict.get(entity).get("entity_id")
                hashvalue = self._get_hash_from_entityid(entity_id)
                friendly_name = statedict.get(entity).get(
                    "attributes").get("friendly_name")
                self._log_debug("Len Callback: %s" % len(f"{entity_id}".encode('utf-8')))
                keyboardrow.append(
                    (count, f"/close_cover?entity_id={hashvalue}"))
                msg += f"{count}: {entity_id} ({friendly_name})\n\n"
                count += 1
                # start a new row after 8 buttons
                # only 8 buttons can be shown in one line (atleast on my phone)
                if count % 8 == 0:
                    keyboard.append(keyboardrow)
                    keyboardrow = list()

        if len(keyboardrow) > 0:
            keyboard.append(keyboardrow)

        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg),
            inline_keyboard=keyboard)

    def _clb_close_cover(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if hashvalue == "all":
            self.call_service("cover/close_cover", entity_id="all")
            msg = "Close all covers!"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
        elif entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Close cover {entity_id} ({friendly_name})"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self.call_service("cover/close_cover",
                              entity_id=entity_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))

    def _cmd_turn_off_light(self, target_id):
        msg = "Which light do you want to turn off?\n"
        statedict = self.get_state()
        keyboard = list()
        keyboardrow = list()
        count = 1
        keyboardrow.append(
            (count, f"/turnoff_light?entity_id=all"))
        msg += f"{count}: Turn off all lights)\n\n"
        count += 1
        for entity in statedict:
            if re.match('^light.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                entity_id = statedict.get(entity).get("entity_id")
                hashvalue = self._get_hash_from_entityid(entity_id)
                friendly_name = statedict.get(entity).get(
                    "attributes").get("friendly_name")
                keyboardrow.append(
                    (count, f"/turnoff_light?entity_id={hashvalue}"))
                msg += f"{count}: {entity_id} ({friendly_name})\n\n"
                count += 1
                # start a new row after 8 buttons
                # only 8 buttins can be shown in one line (atleast on my phone)
                if count % 8 == 0:
                    keyboard.append(keyboardrow)
                    keyboardrow = list()

        if len(keyboardrow) > 0:
            keyboard.append(keyboardrow)

        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg),
            inline_keyboard=keyboard)

    def _clb_turn_off_light(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if hashvalue == "all":
            self.call_service("light/turn_off", entity_id="all")
            msg = "Turn off all lights!"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
        elif entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Turn off light {entity_id} ({friendly_name})"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self.call_service("light/turn_off",
                              entity_id=entity_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))

    def _cmd_turn_on_light(self, target_id):
        msg = "Which light do you want to turn on?\n"
        statedict = self.get_state()
        keyboard = list()
        keyboardrow = list()
        count = 1
        keyboardrow.append(
            (count, f"/turnon_light?entity_id=all"))
        msg += f"{count}: Turn on all lights)\n\n"
        count += 1
        for entity in statedict:
            if re.match('^light.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                entity_id = statedict.get(entity).get("entity_id")
                hashvalue = self._get_hash_from_entityid(entity_id)
                friendly_name = statedict.get(entity).get(
                    "attributes").get("friendly_name")
                keyboardrow.append(
                    (count, f"/turnon_light?entity_id={hashvalue}"))
                msg += f"{count}: {entity_id} ({friendly_name})\n\n"
                count += 1
                # start a new row after 8 buttons
                # only 8 buttins can be shown in one line (atleast on my phone)
                if count % 8 == 0:
                    keyboard.append(keyboardrow)
                    keyboardrow = list()

        if len(keyboardrow) > 0:
            keyboard.append(keyboardrow)

        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg),
            inline_keyboard=keyboard)

    def _clb_turn_on_light(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if hashvalue == "all":
            self.call_service("light/turn_on", entity_id="all")
            msg = "Turn on all lights!"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
        elif entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Turn on light {entity_id} ({friendly_name})"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self.call_service("light/turn_on",
                              entity_id=entity_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id,
                show_alert=True)

    def _cmd_restart_hass(self, target_id):
        msg = "Restart hass?"
        keyboard = [[("Yes", "/restart_hass?value=yes"), ("No",
                                                          "/restart_hass?value=no")]]
        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg),
            inline_keyboard=keyboard)

    def _cmd_start_vacuum(self, target_id):
        msg = "Which vacuum do you want to start?\n"
        statedict = self.get_state()
        keyboard = list()
        keyboardrow = list()
        count = 1
        for entity in statedict:
            if re.match('^vacuum.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                entity_id = statedict.get(entity).get("entity_id")
                hashvalue = self._get_hash_from_entityid(entity_id)
                state = statedict.get(entity).get("state")
                friendly_name = statedict.get(entity).get(
                    "attributes").get("friendly_name")
                battery_level = statedict.get(entity).get(
                    "attributes").get("battery_level")
                keyboardrow.append(
                    (count, f"/start_vacuum?entity_id={hashvalue}"))
                msg += f"{count}: {entity_id} ({friendly_name})\nstate: {state}\nbattery_level: {battery_level}\n\n"
                count += 1
                # start a new row after 8 buttons
                # only 8 buttins can be shown in one line (atleast on my phone)
                if count % 8 == 0:
                    keyboard.append(keyboardrow)
                    keyboardrow = list()

        if len(keyboardrow) > 0:
            keyboard.append(keyboardrow)

        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg),
            inline_keyboard=keyboard)

    def _clb_start_vacuum(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Starting vacuum {entity_id} ({friendly_name})"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self.call_service("vacuum/start",
                              entity_id=entity_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id,
                show_alert=True)

    def _cmd_stop_vacuum(self, target_id):
        msg = "Which vacuum do you want to stop?\n"
        statedict = self.get_state()
        keyboard = list()
        keyboardrow = list()
        count = 1
        for entity in statedict:
            if re.match('^vacuum.*', entity, re.IGNORECASE):
                self._log_debug(statedict.get(entity))
                entity_id = statedict.get(entity).get("entity_id")
                hashvalue = self._get_hash_from_entityid(entity_id)
                state = statedict.get(entity).get("state")
                friendly_name = statedict.get(entity).get(
                    "attributes").get("friendly_name")
                battery_level = statedict.get(entity).get(
                    "attributes").get("battery_level")

                msg += f"{entity_id} {friendly_name}\nstate: {state}\nbattery_level: {battery_level}\n\n"
                keyboardrow.append(
                    (count, f"/stop_vacuum?entity_id={hashvalue}"))
                msg += f"{count}: {entity_id} ({friendly_name})\nstate: {state}\nbattery_level: {battery_level}\n\n"
                count += 1
                # start a new row after 8 buttons
                # only 8 buttins can be shown in one line (atleast on my phone)
                if count % 8 == 0:
                    keyboard.append(keyboardrow)
                    keyboardrow = list()

        if len(keyboardrow) > 0:
            keyboard.append(keyboardrow)

        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg),
            inline_keyboard=keyboard)

    def _clb_stop_vacuum(self, target_id, paramdict):
        hashvalue = paramdict.get("entity_id")
        entity_id = self._get_entityid_from_hash(hashvalue)
        if entity_id is not None:
            friendly_name = self.get_state(entity_id, attribute="friendly_name")
            msg=f"Stopping vacuum {entity_id} ({friendly_name})"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))
            self.call_service("vacuum/return_to_base",
                              entity_id=entity_id)
        else:
            msg = "Unkown entity. Please do not resent old commands!"
            self.call_service(
                'telegram_bot/send_message',
                target=target_id,
                message=self._escape_markdown(msg))

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

    def _clb_restart_hass(self, target_id, paramdict):
        if paramdict.get("value") and paramdict.get("value").lower() == "yes":
            msg = "Restarting hass!"
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id,
                show_alert=True)
            self.call_service(
                'telegram_bot/send_message',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self.call_service(
                'homeassistant/restart')
        elif paramdict.get("value") and paramdict.get("value").lower() == "no":
            msg = "Ok. Not restarting hass!"
            self.call_service(
                'telegram_bot/answer_callback_query',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
            self.call_service(
                'telegram_bot/send_message',
                message=self._escape_markdown(msg),
                callback_query_id=target_id)
        else:
            msg = "Missing value!"
            self.call_service(
                'telegram_bot/send_message',
                message=self._escape_markdown(msg),
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
        
        statedict = self.get_state()
        for entity in statedict:
            if re.match(f"^sensor.({'|'.join(sensorlist)}).*", entity, re.IGNORECASE):
                filtered=False
                if self._filter_state_system is not None and re.search(self._filter_state_system, entity, re.IGNORECASE):
                    #check if entity is filtered 
                    filtered=True
                if not filtered:
                    state = self.get_state(entity)
                    friendly_name=self.get_state(entity, attribute='friendly_name')
                    unit_of_measurement=self.get_state(entity, attribute='unit_of_measurement')
                    if state is not None:
                        msg+=f"{friendly_name}: {state}{unit_of_measurement}\n"
        
        for sensor in self._extend_state_system:
            s = sensor.strip()
            self._log_debug(s)
            state = self.get_state(s)
            friendly_name=self.get_state(s, attribute='friendly_name')
            unit_of_measurement=self.get_state(s, attribute='unit_of_measurement')
            if unit_of_measurement is None:
                unit_of_measurement=""
            if state is not None:
                msg+=f"{friendly_name}: {state}{unit_of_measurement}\n"

        self._log_debug(msg)
        self.call_service(
            'telegram_bot/send_message',
            target=target_id,
            message=self._escape_markdown(msg))
            