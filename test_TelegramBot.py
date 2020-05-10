import mock
import pytest
from datetime import datetime, timedelta
from TelegramBot import TelegramBot
import logging
from unittest.mock import ANY
from freezegun import freeze_time
import hashlib


class TestTelegramBot:

    
    
#    @automation_fixture(TelegramBot)
    @pytest.fixture
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def telegrambot(self, given_that, assert_that):
        telegrambot = TelegramBot(None, TelegramBot.__name__, None, None, None, None, None)

        # Set initial state
        coverlist = ['living_room', 'guest_room', 'parents_room', 'kids_room']
        for cover in coverlist:
            given_that.state_of(f"cover.{cover}").is_set_to(
                "closed", {'friendly_name': f"{cover}", 'current_position': 0})

        lightlist = ['living_room', 'guest_room', 'parents_room', 'kids_room']
        for light in lightlist:
            given_that.state_of(f"light.{light}").is_set_to(
                "off", {'friendly_name': f"{light}"})

        vacuumlist = ['living_room', 'guest_room', 'parents_room', 'kids_room']
        for vacuum in vacuumlist:
            given_that.state_of(f"vacuum.{vacuum}").is_set_to(
                "docked", {'friendly_name': f"{vacuum}", 'battery_level': 2.3})

        climatelist = ['living_room', 'guest_room', 'parents_room', 'kids_room']
        for climate in climatelist:
            given_that.state_of(f"climate.{climate}").is_set_to(
                "auto", {'friendly_name': f"{climate}", 'temperature': 17, 'current_temperature': 20})

        personlist = ['christopher', 'antonia', 'emilia', 'mina']
        for person in personlist:
            given_that.state_of(f"person.{person}").is_set_to(
                "home", {'friendly_name': f"{person}", 'latitude' : 52.5097612943, 'longitude': 13.3732985068, 'gps_accuracy': 20})

        sensorlist = [ 'load_1m',
                        'load_5m',
                        'load_15m',
                        'network_in',
                        'throughput_network_in',
                        'fritz_netmonitor_transmission_rate_down',
                        'fritz_netmonitor_transmission_rate_up']
        for sensor in sensorlist:
            given_that.state_of(f"sensor.{sensor}").is_set_to(
                5, {'friendly_name': f"{sensor}", 'unit_of_measurement' : "%"})

        # set namespace
        telegrambot.set_namespace(None)

        # passed args
        given_that.passed_arg('debug').is_set_to('True')
        given_that.passed_arg('extend_system').is_set_to("sensor.fritz_netmonitor_transmission_rate_down,sensor.fritz_netmonitor_transmission_rate_up")
        given_that.passed_arg('filter_blacklist').is_set_to(["network_in", "parents_room", "mina"])
        telegrambot.initialize()

        assert_that(telegrambot) \
        .listens_to.event('telegram_command') \
        .with_callback(telegrambot._receive_telegram_command)

        assert_that(telegrambot) \
        .listens_to.event('telegram_callback') \
        .with_callback(telegrambot._receive_telegram_callback)

        given_that.mock_functions_are_cleared()
        return telegrambot

    # _receive_telegram_command
    # Fall1: command=/help
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__receive_telegram_command_case1(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        chat_id = 1
        command = "/help"
        payload_event = dict()
        payload_event.update({"user_id": user_id})
        payload_event.update({"chat_id": chat_id})
        payload_event.update({"command": command})

        telegrambot._receive_telegram_command(None, payload_event)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=ANY, inline_keyboard=ANY)

    # _receive_telegram_command
    # Fall2: command=/doesnotexits
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__receive_telegram_command_case2(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        chat_id = 1
        command = "/doesnotexits"
        payload_event = dict()
        payload_event.update({"user_id": user_id})
        payload_event.update({"chat_id": chat_id})
        payload_event.update({"command": command})

        telegrambot._receive_telegram_command(None, payload_event)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=ANY)

    # _receive_telegram_command
    # Fall3: command=/state_cover
    # command exists
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__receive_telegram_command_case3(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        chat_id = 1
        command = "/state_cover"
        payload_event = dict()
        payload_event.update({"user_id": user_id})
        payload_event.update({"chat_id": chat_id})
        payload_event.update({"command": command})

        telegrambot._cmd_state_cover = mock.MagicMock()

        telegrambot._receive_telegram_command(None, payload_event)
        
        assert_that(
            'telegram_bot/send_message').was.called_with(target=ANY, message=ANY)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__escape_markdown(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        
        assert telegrambot._escape_markdown("Test Escape Markdown ` * _") == "Test Escape Markdown \\` \\* \\_"


    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_state_cover(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        given_that.passed_arg('filter_blacklist').is_set_to(['guest_room', 'parents_room', 'kids_room'])
        telegrambot.initialize()

        entity_id="cover.living_room"
        friendly_name="living_room"
        state="closed"
        current_position=0
        msg = telegrambot._escape_markdown(f"{friendly_name}\nstate: {state}\ncurrent_position: {current_position}\n\n")

        telegrambot._cmd_state_cover(user_id)
        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_state_person(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        given_that.passed_arg('filter_blacklist').is_set_to(['antonia', 'emilia', 'mina'])
        telegrambot.initialize()

        entity_id="person.christopher"
        friendly_name="christopher"
        state="home"
        latitude=52.5097612943
        longitude=13.3732985068
        gps_accuracy=20
        msg = telegrambot._escape_markdown(f"{friendly_name}\nstate: {state}\nlatitude: {latitude}\nlongitude: {longitude}\ngps_accuracy: {gps_accuracy}\n\n")

        telegrambot._cmd_state_person(user_id)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)
        assert_that(
            'telegram_bot/send_location').was.called_with(target=user_id, latitude=latitude, longitude=longitude)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_state_vacuum(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        given_that.passed_arg('filter_blacklist').is_set_to(['guest_room', 'parents_room', 'kids_room'])
        telegrambot.initialize()

        entity_id="vacuum.living_room"
        friendly_name="living_room"
        state="docked"
        battery_level=2.3
        msg = telegrambot._escape_markdown(f"{friendly_name}\nstate: {state}\nbattery_level: {battery_level}\n\n")

        telegrambot._cmd_state_vacuum(user_id)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_state_light(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        given_that.passed_arg('filter_blacklist').is_set_to(['guest_room', 'parents_room', 'kids_room'])
        telegrambot.initialize()

        entity_id="light.living_room"
        friendly_name="living_room"
        state="off"
        msg = telegrambot._escape_markdown(f"{friendly_name}\nstate: {state}\n\n")

        telegrambot._cmd_state_light(user_id)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)


    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_state_climate(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        given_that.passed_arg('filter_blacklist').is_set_to(['guest_room', 'parents_room', 'kids_room'])
        telegrambot.initialize()

        entity_id="climate.living_room"
        friendly_name="living_room"
        state="auto"
        current_temperature=20
        temperature=17
        msg = telegrambot._escape_markdown(f"{friendly_name}\nstate: {state}\ncurrent temperature: {current_temperature}\ntemperature: {temperature}.\n\n")

        telegrambot._cmd_state_climate(user_id)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

    #case 1 hashvalue=all
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_open_cover_case1(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"entity_id":"all"})

        msg = telegrambot._escape_markdown("Open all covers!")

        telegrambot._clb_open_cover(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=msg, callback_query_id=user_id)

        assert_that(
            'cover/open_cover').was.called_with(entity_id="all")

    #case 2 hashvalue=hash("cover.entity_id")
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_open_cover_case2(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        entity_id="cover.living_room"
        friendly_name="living_room"
        hashvalue = telegrambot._get_hash_from_entityid(entity_id)
        paramdict = dict()
        paramdict.update({"entity_id": hashvalue})

        msg = telegrambot._escape_markdown(f"Open cover {entity_id} ({friendly_name})")

        telegrambot._clb_open_cover(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)
        
        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=msg, callback_query_id=user_id)

        assert_that(
            'cover/open_cover').was.called_with(entity_id=entity_id)

    #case 3 hashvalue=unkown
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_open_cover_case3(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"entity_id": "unkown"})
        msg = telegrambot._escape_markdown(f"Unkown entity. Please do not resent old commands!")
        telegrambot._clb_open_cover(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)


    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_open_cover(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        given_that.passed_arg('filter_blacklist').is_set_to(['guest_room', 'parents_room', 'kids_room'])
        telegrambot.initialize()

        entity_id="cover.living_room"
        friendly_name="living_room"
        state="closed"
        msg = telegrambot._escape_markdown(f"Which cover do you want to open?\n\n1: Open all covers\n2: {friendly_name}\n")

        keyboard = list()
        keyboardrow = list()
        keyboardrow.append(
            (1, f"/clb_open_cover?entity_id=all"))
        hashvalue = telegrambot._get_hash_from_entityid(f"{entity_id}")
        keyboardrow.append(
            (2, f"/clb_open_cover?entity_id={hashvalue}"))
        keyboard.append(keyboardrow)
        telegrambot._cmd_open_cover(user_id)    

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg, inline_keyboard=keyboard)


    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_close_cover(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        given_that.passed_arg('filter_blacklist').is_set_to(['guest_room', 'parents_room', 'kids_room'])
        telegrambot.initialize()

        entity_id="cover.living_room"
        friendly_name="living_room"
        state="closed"
        msg = telegrambot._escape_markdown(f"Which cover do you want to close?\n\n1: Close all covers\n2: {friendly_name}\n")

        keyboard = list()
        keyboardrow = list()
        keyboardrow.append(
            (1, f"/clb_close_cover?entity_id=all"))
        hashvalue = telegrambot._get_hash_from_entityid(f"{entity_id}")
        keyboardrow.append(
            (2, f"/clb_close_cover?entity_id={hashvalue}"))
        keyboard.append(keyboardrow)
        telegrambot._cmd_close_cover(user_id)    

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg, inline_keyboard=keyboard)

    #case 1 hashvalue=all
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_close_cover_case1(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"entity_id":"all"})

        msg = telegrambot._escape_markdown("Close all covers!")

        telegrambot._clb_close_cover(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=msg, callback_query_id=user_id)

        assert_that(
            'cover/close_cover').was.called_with(entity_id="all")

    #case 2 hashvalue=hash("cover.entity_id")
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_close_cover_case2(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        entity_id="cover.living_room"
        friendly_name="living_room"
        hashvalue = telegrambot._get_hash_from_entityid(entity_id)
        paramdict = dict()
        paramdict.update({"entity_id": hashvalue})

        msg = telegrambot._escape_markdown(f"Close cover {entity_id} ({friendly_name})")

        telegrambot._clb_close_cover(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)
        
        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=msg, callback_query_id=user_id)

        assert_that(
            'cover/close_cover').was.called_with(entity_id=entity_id)

    #case 3 hashvalue=unkown
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_close_cover_case3(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"entity_id": "unkown"})
        msg = telegrambot._escape_markdown(f"Unkown entity. Please do not resent old commands!")
        telegrambot._clb_close_cover(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)
    
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_turn_off_light(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        given_that.passed_arg('filter_blacklist').is_set_to(['guest_room', 'parents_room', 'kids_room'])
        telegrambot.initialize()

        entity_id="light.living_room"
        friendly_name="living_room"
        state="off"
        msg = telegrambot._escape_markdown(f"Which light do you want to turn off?\n\n1: Turn off all lights\n2: {friendly_name}\n")

        keyboard = list()
        keyboardrow = list()
        keyboardrow.append(
            (1, f"/clb_turnoff_light?entity_id=all"))
        hashvalue = telegrambot._get_hash_from_entityid(f"{entity_id}")
        keyboardrow.append(
            (2, f"/clb_turnoff_light?entity_id={hashvalue}"))
        keyboard.append(keyboardrow)
        telegrambot._cmd_turn_off_light(user_id)    

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg, inline_keyboard=keyboard)

    #case 1 hashvalue=all
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_turn_off_light_case1(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"entity_id":"all"})

        msg = telegrambot._escape_markdown("Turn off all lights!")

        telegrambot._clb_turn_off_light(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=msg, callback_query_id=user_id)

        assert_that(
            'light/turn_off').was.called_with(entity_id="all")

    #case 2 hashvalue=hash("cover.entity_id")
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_turn_off_light_case2(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        entity_id="cover.living_room"
        friendly_name="living_room"
        hashvalue = telegrambot._get_hash_from_entityid(entity_id)
        paramdict = dict()
        paramdict.update({"entity_id": hashvalue})

        msg = telegrambot._escape_markdown(f"Turn off light {entity_id} ({friendly_name})")

        telegrambot._clb_turn_off_light(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)
        
        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=msg, callback_query_id=user_id)

        assert_that(
            'light/turn_off').was.called_with(entity_id=entity_id)

    #case 3 hashvalue=unkown
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_turn_off_light_case3(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"entity_id": "unkown"})
        msg = telegrambot._escape_markdown(f"Unkown entity. Please do not resent old commands!")
        telegrambot._clb_turn_off_light(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_turn_on_light(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        given_that.passed_arg('filter_blacklist').is_set_to(['guest_room', 'parents_room', 'kids_room'])
        telegrambot.initialize()

        entity_id="light.living_room"
        friendly_name="living_room"
        state="off"
        msg = telegrambot._escape_markdown(f"Which light do you want to turn on?\n\n1: Turn on all lights\n2: {friendly_name}\n")

        keyboard = list()
        keyboardrow = list()
        keyboardrow.append(
            (1, f"/clb_turnon_light?entity_id=all"))
        hashvalue = telegrambot._get_hash_from_entityid(f"{entity_id}")
        keyboardrow.append(
            (2, f"/clb_turnon_light?entity_id={hashvalue}"))
        keyboard.append(keyboardrow)
        telegrambot._cmd_turn_on_light(user_id)    

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg, inline_keyboard=keyboard)

    #case 1 hashvalue=all
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_turn_on_light_case1(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"entity_id":"all"})

        msg = telegrambot._escape_markdown("Turn on all lights!")

        telegrambot._clb_turn_on_light(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

        assert_that(
            'light/turn_on').was.called_with(entity_id="all")
        
        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=msg, callback_query_id=user_id)

    #case 2 hashvalue=hash("cover.entity_id")
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_turn_on_light_case2(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        entity_id="cover.living_room"
        friendly_name="living_room"
        hashvalue = telegrambot._get_hash_from_entityid(entity_id)
        paramdict = dict()
        paramdict.update({"entity_id": hashvalue})

        msg = telegrambot._escape_markdown(f"Turn on light {entity_id} ({friendly_name})")

        telegrambot._clb_turn_on_light(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)
        
        assert_that(
            'light/turn_on').was.called_with(entity_id=entity_id)
        
        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=msg, callback_query_id=user_id)

    #case 3 hashvalue=unkown
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_turn_on_light_case3(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"entity_id": "unkown"})
        msg = telegrambot._escape_markdown(f"Unkown entity. Please do not resent old commands!")
        telegrambot._clb_turn_off_light(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_restart_hass(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        msg = "Restart home-assistant?"
        keyboard = [[("Yes", "/clb_restart_hass?value=yes"), ("No",
                                                          "/clb_restart_hass?value=no")]]
        telegrambot._cmd_restart_hass(user_id)    

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg, inline_keyboard=keyboard)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_start_vacuum(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        given_that.passed_arg('filter_blacklist').is_set_to(['guest_room', 'parents_room', 'kids_room'])
        telegrambot.initialize()

        entity_id="vacuum.living_room"
        friendly_name="living_room"
        state="docked"
        count=1
        battery_level=2.3
        msg = telegrambot._escape_markdown(f"Which vacuum do you want to start?\n\n{count}: {friendly_name}\nstate: {state}\nbattery_level: {battery_level}\n")

        keyboard = list()
        keyboardrow = list()
        hashvalue = telegrambot._get_hash_from_entityid(f"{entity_id}")
        keyboardrow.append(
            (1, f"/clb_start_vacuum?entity_id={hashvalue}"))
        keyboard.append(keyboardrow)
        telegrambot._cmd_start_vacuum(user_id)    

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg, inline_keyboard=keyboard)

    #case 1 hashvalue=hash("cover.entity_id")
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_start_vacuum_case1(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        entity_id="vacuum.living_room"
        friendly_name="living_room"
        hashvalue = telegrambot._get_hash_from_entityid(entity_id)
        paramdict = dict()
        paramdict.update({"entity_id": hashvalue})

        msg = telegrambot._escape_markdown(f"Starting vacuum {entity_id} ({friendly_name})")

        telegrambot._clb_start_vacuum(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

        assert_that(
            'vacuum/start').was.called_with(entity_id=entity_id)
        
        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=msg, callback_query_id=user_id)

    #case 2 hashvalue=unkown
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_start_vacuum_case2(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"entity_id": "unkown"})
        msg = telegrambot._escape_markdown(f"Unkown entity. Please do not resent old commands!")
        telegrambot._clb_start_vacuum(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_stop_vacuum(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        given_that.passed_arg('filter_blacklist').is_set_to(['guest_room', 'parents_room', 'kids_room'])
        telegrambot.initialize()

        entity_id="vacuum.living_room"
        friendly_name="living_room"
        state="docked"
        count=1
        battery_level=2.3
        msg = telegrambot._escape_markdown(f"Which vacuum do you want to stop?\n\n{count}: {friendly_name}\nstate: {state}\nbattery_level: {battery_level}\n")

        keyboard = list()
        keyboardrow = list()
        hashvalue = telegrambot._get_hash_from_entityid(f"{entity_id}")
        keyboardrow.append(
            (1, f"/clb_stop_vacuum?entity_id={hashvalue}"))
        keyboard.append(keyboardrow)
        telegrambot._cmd_stop_vacuum(user_id)    

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg, inline_keyboard=keyboard)

    #case 1 hashvalue=hash("cover.entity_id")
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_stop_vacuum_case1(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        entity_id="vacuum.living_room"
        friendly_name="living_room"
        hashvalue = telegrambot._get_hash_from_entityid(entity_id)
        paramdict = dict()
        paramdict.update({"entity_id": hashvalue})

        msg = telegrambot._escape_markdown(f"Stopping vacuum {entity_id} ({friendly_name})")

        telegrambot._clb_stop_vacuum(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)
        
        assert_that(
            'vacuum/return_to_base').was.called_with(entity_id=entity_id)
        
        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=msg, callback_query_id=user_id)

    #case 2 hashvalue=unkown
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_stop_vacuum_case2(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"entity_id": "unkown"})
        msg = telegrambot._escape_markdown(f"Unkown entity. Please do not resent old commands!")
        telegrambot._clb_stop_vacuum(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_restart_hass_case1(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"value": "yes"})

        msg = telegrambot._escape_markdown(f"Restarting home-assistant!")

        telegrambot._clb_restart_hass(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)
        
        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=msg, callback_query_id=user_id, show_alert=True)

        assert_that(
            'homeassistant/restart').was.called()

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_restart_hass_case2(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"value": "no"})

        msg = telegrambot._escape_markdown(f"Ok. Not restarting home-assistant!")

        telegrambot._clb_restart_hass(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)
        
        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=msg, callback_query_id=user_id)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_restart_hass_case3(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"value": "unkown"})

        msg = telegrambot._escape_markdown(f"Missing value!")

        telegrambot._clb_restart_hass(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__get_hash_from_entityid(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        entity_id="cover.living_room"
        h = hashlib.md5(entity_id.encode('utf-8')).hexdigest()

        assert telegrambot._get_hash_from_entityid(entity_id) == h

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__get_entityid_from_hash(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        entity_id="cover.living_room"

        h = telegrambot._get_hash_from_entityid(entity_id)
        assert telegrambot._get_entityid_from_hash(h) == entity_id

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__homeassistant_update_available(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        entity_id="binary_sensor.updater"

        given_that.state_of(f"binary_sensor.updater").is_set_to(
                "on", {'friendly_name': f"Updater", 'newest_version': "0.109.3", 'release_notes': "https://www.home-assistant.io/latest-release-notes/"})
        
        msg = telegrambot._escape_markdown(f"Home-assistant update available! Newest version: 0.109.3.\n Release Notes: https://www.home-assistant.io/latest-release-notes/")
        
        telegrambot._homeassistant_update_available(entity_id, "state", "off", "on", None)

        assert_that(
            'telegram_bot/send_message').was.called_with(message=msg)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__homeassistant_restarted(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        msg = telegrambot._escape_markdown(f"Home-assistant restarted!")

        telegrambot._homeassistant_restarted(None, None)

        assert_that(
            'telegram_bot/send_message').was.called_with(message=msg)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__appdaemon_restarted(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        msg = telegrambot._escape_markdown(f"Appdaemon restarted!")

        telegrambot._appdaemon_restarted(None, None)

        assert_that(
            'telegram_bot/send_message').was.called_with(message=msg)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_state_system(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        given_that.passed_arg('filter_blacklist').is_set_to(['load_5m', 'load_15m', 'network_in', 'throughput_network_in'])
        telegrambot.initialize()

        sensorlist = [ 'load_1m',
                        'fritz_netmonitor_transmission_rate_down',
                        'fritz_netmonitor_transmission_rate_up']

        msg=""
        for sensor in sensorlist:
            entity_id=f"sensor.{sensor}"
            friendly_name=sensor
            state=5
            unit_of_measurement="%"
            msg += f"{friendly_name}: {state}{unit_of_measurement}\n"

        msg = telegrambot._escape_markdown(msg)

        telegrambot._cmd_state_system(user_id)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__cmd_get_version(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1

        msg = telegrambot._escape_markdown(f"TelegramBot Version: {telegrambot._version}")

        telegrambot._cmd_get_version(user_id)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=msg)