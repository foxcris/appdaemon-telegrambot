# appdaemon-telegrambot

Simple bot to control your home-assistant via a telegram chatbot.
As a requirement, the telegram platform has to be configured in home-assistant (https://www.home-assistant.io/components/notify.telegram/).

Currently the bot provides a simple request/response command interface. The following commands are available:
* /help
* /state_cover: State of cover
* /state_vacuum: State of vacuum
* /state_light: State of light
* /state_climate: State of climate
* /state_person: State of person
* /open_cover: Open cover
* /close_cover: Close cover
* /turnoff_light: Turn off light
* /turnon_light: Turn on light
* /start_vacuum: Start vacuum
* /stop_vacuum: Stop running vacuum
* /restart_hass: Restart hass
* /state_system: State of home-assistant
* /get_version: Get version of telegrambot

## Configuration
### appdaemon configuration
Just copy the files
* TelegramBot.py
* Helper.py

to your apps folder of appaemon and add the following configuration to your apps.yaml (example data shown for some parameters)
```
TelegramBot:
  module:                   TelegramBot
  class:                    TelegramBot
  debug:                    True
  extend_system:            sensor.date,sensor.heartbeat
  filter_exclude_system:    (load_1m|load5m)
  filter_exclude_cover:     (bathroom)
  filter_exclude_vacuum:    (xiaomi)
  filter_exclude_light:     (fireplace)
  filter_exclude_climate:   (guestroom)
  filter_exclude_person:    (john)
```

extend_system: comma separated list of complete entities to include in the system report
filter_exclude_*: python regex to exclude entities from being reported/used from telegrambot

The file Helper.py is also used by one of my [other](https://github.com/foxcris/appdaemon-blinds-control) appdaemon project. In both projects the same file is used!
### home-assistant configuration

# Screenshots
<img src="https://raw.githubusercontent.com/foxcris/appdaemon-telegrambot/master/images/Screenshot_20190310_123130_org.telegram.messenger.jpg" width="250">
<img src="https://raw.githubusercontent.com/foxcris/appdaemon-telegrambot/master/images/Screenshot_20190403_210457_org.telegram.messenger.jpg" width="250">
<img src="https://raw.githubusercontent.com/foxcris/appdaemon-telegrambot/master/images/Screenshot_20190403_210508_org.telegram.messenger.jpg" width="250">
<img src="https://raw.githubusercontent.com/foxcris/appdaemon-telegrambot/master/images/Screenshot_20190403_210559_org.telegram.messenger.jpg" width="250">
