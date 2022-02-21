# appdaemon-telegrambot

Simple bot to control your home-assistant via a telegram chatbot.
As a requirement, the telegram platform has to be configured in home-assistant (https://www.home-assistant.io/components/notify.telegram/).

Currently the bot provides a simple request/response command interface. The following commands are available:
* /help: Help
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
* /state_sensor: State of sensors
* /get_version: Get version of telegrambot
* /turnon_automation: Turn on automation
* /turnoff_automation: Turn off automation
* /trigger_automation: Trigger automation
* /state_automation: State of automation
* send location message from telegram: for each defined zone in home-assistant the travel time from the current location sent is computed

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
  extend_light:             switch.light
  filter_blacklist:
    - unwanted_entity
    - another_unwanted_entity
  filter_whitelist:
    - sample
  routing:
    waze:
      region:               EU
      avoid_toll_roads:     True
  ```

||Configuration parameter || Description ||
|extend_system | comma separated list of complete entities to include in the system report|
|extend_light | comma separated list of complete entities to include in the commands /state_light /turnoff_light /turnon_light|
|filter_blacklist| List of python regex to exclude entities from being reported/used from telegrambot. As the most simple regex you can just list all entities you want to remove.|
|filter_whitelist| List of python regex to whitelist entities from being reported/used from telegrambot. Becareful, mosttime you do not want to use this!
The following logic is used to apply the blacklist and whitelist:
* If the blacklist is empty - nothing is filtered out
* If the whitelist is empty - nothing is filtered out
* If both the blacklist and whitelist are non-empty, first the blacklist ist applied and then the whitelist
|
|routing| currently only waze is supported. region can be 'US','EU','IL','AU' and is used to select the correct routingserver from waze. avoid_toll_roads is a boolean to enable/disable the use of toll roads in the travel time computation.|

The file Helper.py is also used by one of my [other](https://github.com/foxcris/appdaemon-blinds-control) appdaemon project. In both projects the same file is used!

## Screenshots
<img src="https://raw.githubusercontent.com/foxcris/appdaemon-telegrambot/master/images/Screenshot_20190310_123130_org.telegram.messenger.jpg" width="250">
<img src="https://raw.githubusercontent.com/foxcris/appdaemon-telegrambot/master/images/Screenshot_20190403_210457_org.telegram.messenger.jpg" width="250">
<img src="https://raw.githubusercontent.com/foxcris/appdaemon-telegrambot/master/images/Screenshot_20190403_210508_org.telegram.messenger.jpg" width="250">
<img src="https://raw.githubusercontent.com/foxcris/appdaemon-telegrambot/master/images/Screenshot_20190403_210559_org.telegram.messenger.jpg" width="250">

## Contributing

* All contributions are welcome!
* A PR must be accompanied with some tests for the new feature
* Please take care that:
  * The code is readable and is optimally documented
  * The code passes all tests

### Tests

For the unit test the [Appdamon-Test-Framework](https://github.com/FlorianKempenich/Appdaemon-Test-Framework) is used together with [pytest](https://docs.pytest.org/en/latest/).

### Requirements

All necessary requirements are listed in the `pyproject.toml`.