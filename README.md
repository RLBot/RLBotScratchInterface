# RLBotScratchInterface
Allows the Scratch programming language to control RLBot.

## Video Guide

https://youtu.be/3e-n52_Tb6k

## Split Screen Instructions

If you want to show multiple cars in a split screen view, follow these instructions.

1. Make sure you've installed [Python 3.6 64 bit](https://www.python.org/ftp/python/3.6.5/python-3.6.5-amd64.exe). During installation:
   - Select "Add Python to PATH"
   - Don't opt out of pip
1. Download this repository
1. Install [vJoy](http://vjoystick.sourceforge.net)
1. Find the vJoy installation directory and copy x64/vJoyInterface.dll
into the pyvjoy folder located here.
1. Run the "Configure vJoy" application and add additional controllers until you have four.
1. Set up x360ce
   - Download [x360ce](https://www.x360ce.com/) 32-bit - [direct link](https://github.com/x360ce/x360ce/blob/master/x360ce.Web/Files/x360ce.zip?raw=true)
   - Copy the .exe into your Rocket League installation directory. You can find the directory by following the first three steps [here](https://steamcommunity.com/sharedfiles/filedetails/?id=760447682).
   - Double click the .exe and allow it to set up the four controllers. Save and exit.
1. Open Rocket League
1. Double click on start_party.bat, and then quickly tab into Rocket League
so that it receives the button presses that are about to be sent.
Multiple local players should be seen joining the party.
1. Double click on run.bat
1. Visit http://scratch.rlbot.org
