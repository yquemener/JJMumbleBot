# JJMumbleBot
[![GitHub release](https://img.shields.io/github/release/DuckBoss/JJMumbleBot.svg)](https://github.com/DuckBoss/JJMumbleBot/releases/latest)
[![Packagist](https://img.shields.io/badge/License-GPL-blue.svg)](https://github.com/DuckBoss/JJMumbleBot/blob/master/LICENSE)
<br>
[![CodeFactor](https://www.codefactor.io/repository/github/duckboss/jjmumblebot/badge)](https://www.codefactor.io/repository/github/duckboss/jjmumblebot)
[![Build Status](https://travis-ci.com/DuckBoss/JJMumbleBot.svg?branch=master)](https://travis-ci.com/DuckBoss/JJMumbleBot)

A plugin-based All-In-One mumble bot solution in python 3.7+ with extensive features and support for custom plugins.


## Features  🚀 
- <b>Built-in Plugins</b> - Fast, responsive, plugin-based system for easy expandability.
  - <b>Youtube Plugin</b> - Streams youtube songs in the channel.
    - Playlist Support
    - Video Thumbnails
    - Queue System
    - Direct Youtube Link Support
    - Search/Browse Youtube Support
    - Whisper Support
  - <b>Images Plugin</b> - Posts images from urls or from a local directory in the channel.
    - Local Images Support
    - Direct Link Images Support
  - <b>Sound Board Plugin</b> - Sound Board that plays short wav audio clips in the channel.
    - Local Audio Clips Support
    - Download and Play Support
    - Whisper Support
  - <b>Randomizer Plugin</b> - Do custom dice rolls, coin flips, etc in the channel.
    - Dice Rolls
    - Coin Flips
  - <b>Whisper Plugin</b> - Whisper support for audio data.
  - <b>Bot Commands Plugin</b> - Enhanced interactivity and management commands.
  - <b><a href="https://github.com/DuckBoss/JJMumbleBot/wiki">Full list of built-in plugins</a></b>
- <b>Web Interface [WIP]</b> - Control and manage the bot with an optional web interface.
- <b>Auto-Updater</b> - A System to update dependencies through bot commands.
- <b><a href="https://github.com/DuckBoss/JJMumbleBot/wiki/Plugins">Support for custom plugins</a></b>
- <b>Pseudo-GUI System [PGUI]</b> - A pseudo graphical user interface built with html tags.
- <b>Event logging to keep track of bot usage and command history.</b>
- <b>Multi-Command Input</b> - Input multiple commands in a single line.
- <b>Command Aliases</b> - Register custom aliases to shorten command calls.
- <b>Custom Command Tokens</b> - Custom command recognition tokens (ex: !command, ~command, /command, etc)
- <b>Command Tick Rates</b> - Commands in the queue are processed by the tick rate assigned in the config.
- <b>Multi-Threaded Command Processing</b> - Commands in the queue are handled in multiple threads for faster processing.
- <b>Reconfigurable Command Privileges</b> - The user privileges required to execute commands can be completely reconfigured.

## Installation And Setup 🏃
- Download and install python 3.7+
    - Linux: `sudo apt-get install python3.7`
    - Mac OSX: <a href="https://www.python.org/downloads/mac-osx/">Mac OSX Python Downloads</a>
    - Windows: <a href="https://www.python.org/downloads/windows/">Windows Python Downloads</a>
- Install project dependencies
    - `pip install -r requirements.txt`
    - <b>Note: You must have libopus installed and installation varies by operating system.</b>
- Please make sure your murmur server supports sending text messages of over 90000 characters. (Configurable in your murmur.ini file)
- Please check the <a href="https://github.com/DuckBoss/JJMumbleBot/wiki">Wiki Pages</a> for setup procedures and more information.

## Documentation 📝 
<b><a href="https://github.com/DuckBoss/JJMumbleBot/wiki">JJMumbleBot Documentation WIKI</a></b> <br>
<b><a href="https://github.com/DuckBoss/JJMumbleBot/wiki/Frequently-Asked-Questions">F.A.Q - Solve common issues easily</a></b> <br>
<b><a href="https://github.com/DuckBoss/JJMumbleBot/wiki/Requirements">Requirements and Dependencies</a></b> <br>
<b><a href="https://github.com/DuckBoss/JJMumbleBot/wiki/Quick-Start">Quick Start Guide</a></b> <br>
<b><a href="https://duckboss.github.io/JJMumbleBot/pages/qsu.html">Quick Setup Utility - Web Interface For Config.ini File Creation</a></b> <br>
<b><a href="https://github.com/DuckBoss/JJMumbleBot/wiki/LegacyVersions">Legacy Versions</a></b> 

## Extra Plugins:
<a href="https://github.com/DuckBoss/JJMumbleBot-PluginLibrary">https://github.com/DuckBoss/JJMumbleBot-PluginLibrary</a>

### Got any questions or concerns? Please post an issue report 👋 
#### Or email me @ <a href="mailto:duckboss@kakao.com">duckboss@kakao.com</a>
