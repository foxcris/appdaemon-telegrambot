# appdaemon-telegrambot

Simple bot to control your home-assistant via a telegram chatbot.
As a requirements, the telegram platform has to be configured in home-assistant (https://www.home-assistant.io/components/notify.telegram/).

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

## Configuration
### appdaemon configuration
Just copy the files
* TelegramBot.py
* Helper.py

to your apps folder of appaemon and add the following configuration to your apps.yaml
```
TelegramBot:
  module:                   TelegramBot
  class:                    TelegramBot
  debug:                    True
```

The file Helper.py is also used by one of my [other](https://github.com/foxcris/appdaemon-blinds-control) appdaemon project. In both projects the same file is used!
### home-assistant configuration

# Screenshots
![Available commands](https://raw.githubusercontent.com/foxcris/appdaemon-telegrambot/master/images/Screenshot_20190310_123130_org.telegram.messenger.jpg "Available commands")
![State covers](https://raw.githubusercontent.com/foxcris/appdaemon-telegrambot/master/images/Screenshot_20190403_210457_org.telegram.messenger.jpg "State covers")
![State vacuum](https://raw.githubusercontent.com/foxcris/appdaemon-telegrambot/master/images/Screenshot_20190403_210508_org.telegram.messenger.jpg "State vacuum")
![Open cover](https://raw.githubusercontent.com/foxcris/appdaemon-telegrambot/master/images/Screenshot_20190403_210559_org.telegram.messenger.jpg "Open cover")
