import mock
import pytest
from datetime import datetime, timedelta
from TelegramBot import TelegramBot
import logging
from unittest.mock import ANY
from freezegun import freeze_time



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
                "docked", {'friendly_name': f"{vacuum}"})

        # set namespace
        telegrambot.set_namespace(None)

        # passed args
        given_that.passed_arg('debug').is_set_to('True')
        given_that.passed_arg('extend_state_system').is_set_to("sensor.fritz_netmonitor_external_ip,sensor.fritz_netmonitor_transmission_rate_down,sensor.fritz_netmonitor_transmission_rate_up")
        given_that.passed_arg('filter_state_system').is_set_to("network_in")

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
            'telegram_bot/send_message').was.called_with(target=user_id, message=ANY)

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
        telegrambot._cmd_state_cover(user_id)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=ANY)

    #case 1 hashvalue=all
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_open_cover_case1(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"entity_id":"all"})

        telegrambot._clb_open_cover(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=ANY)

        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=ANY, callback_query_id=user_id)

    #case 2 hashvalue=hash("cover.entity_id")
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_open_cover_case2(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        entity_id="cover.living_room"
        hashvalue = telegrambot._get_hash_from_entityid(entity_id)
        paramdict = dict()
        paramdict.update({"entity_id": hashvalue})

        telegrambot._clb_open_cover(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message=ANY)
        
        assert_that(
            'telegram_bot/answer_callback_query').was.called_with(message=ANY, callback_query_id=user_id)

    #case 3 hashvalue=unkown
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test__clb_open_cover_case3(self, given_that, telegrambot, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        user_id = 1
        paramdict = dict()
        paramdict.update({"entity_id": "unkown"})

        telegrambot._clb_open_cover(user_id, paramdict)

        assert_that(
            'telegram_bot/send_message').was.called_with(target=user_id, message="Unkown entity. Please do not resent old commands!")