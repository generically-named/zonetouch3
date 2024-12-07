# Zonetouch 3 Home Assistant Integration
Not actually a HA integration yet...

~~Currently there is only the python program that allows command line control of a ZT3.~~

~~I am working on getting the python program to be a HA integration as the python program is fully capable of everything you'd want in a zone controller.~~

I have now uploaded what I have in terms of a HA integration, I don't believe it is fully functional and do believe it is quite buggy and not at all good enough to submit for merging as part of HA. Maybe [@GeoDerp](https://github.com/GeoDerp) you will find this useful to adapt as part of your HA integration.

See the thread on HA forum for ZoneTouch3 Communication Protocol: https://community.home-assistant.io/t/zonetouch-3-by-polyaire/496405

## A note on control philosophy
It is my belief the integration should mimmick the control of the ZoneTouch3 control panel. That is the user has the ability to enable and disable zones entirely independent of the opening percentage of said zone. This would mean each zone has a switch to turn it on/off and a separate slider that controls how open or closed that zone is.


