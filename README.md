# JJMumbleBot
[![Packagist](https://img.shields.io/badge/License-GPL-blue.svg)](https://github.com/DuckBoss/JJMumbleBot/blob/master/LICENSE)

A plugin-based python 3 mumble bot with extensive features.


## Features
- <b>Built-in Plugins</b> - Fast, responsive, plugin-based system for easy expandability.
  - <b>Youtube Plugin</b> - Streams youtube songs in the channel.
  - <b>Images Plugin</b> - Posts images from urls or from a local directory in the channel.
  - <b>Sound Board Plugin</b> - Sound Board that plays short wav audio clips in the channel.
  - <b>Randomizer Plugin</b> - Do custom dice rolls, coin flips, etc in the channel.
  - <b><a href="https://github.com/DuckBoss/JJMumbleBot/wiki/Quick-Start">Full list of built-in plugins</a></b>
- <b>Support for adding plugins at runtime.</b>
- <b><a href="https://github.com/DuckBoss/JJMumbleBot/wiki/Plugins">Support for custom plugins</a></b>
- <b>Event logging to keep track of bot usage and command history.</b>
- <b>Multi-Command Input</b> - Input multiple commands in a single line.
- <b>Command Aliases</b> - Register custom aliases to shorten command calls.
- <b>Custom Command Tokens</b> - Custom command recognition tokens (ex: !command, ~command, /command, etc)
- <b>Command Tick Rates</b> - Commands in the queue are processed by the tick rate assigned in the config.
- <b>Multi-Threaded Command Processing</b> - Commands in the queue are handled in multiple threads for faster processing.
- <b>Reconfigurable Command Privileges</b> - The user privileges required to execute commands can be completely reconfigured.
