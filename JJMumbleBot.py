import pymumble.pymumble_py3 as pymumble
import time
import os
import sys
import utils
import privileges as pv
import aliases
import logging
from logging.handlers import TimedRotatingFileHandler
from helpers.global_access import GlobalMods as GM
from helpers.global_access import debug_print, reg_print
from helpers.queue_handler import QueueHandler
from helpers.command import Command
from bs4 import BeautifulSoup
import threading
import copy


class JJMumbleBot:
    # Toggles for bot states.
    exit_flag = False
    # Bot status.
    bot_status = "Offline"
    # Dictionary of registered bot plugins.
    bot_plugins = {}
    # Runtime parameters.
    tick_rate = 0.1
    multi_cmd_limit = 5
    cmd_token = None

    def __init__(self):
        print("JJ Mumble Bot Initializing...")
        # Initialize configs.
        GM.cfg.read(utils.get_config_dir())
        # Initialize application logging.
        logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)
        log_file_name = '%s/runtime.log' % GM.cfg['Bot_Directories']['LogDirectory']
        GM.logger = logging.getLogger(log_file_name)
        GM.logger.setLevel(logging.CRITICAL)

        log_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
        handler = TimedRotatingFileHandler(log_file_name, when='midnight', backupCount=30)
        handler.setLevel(logging.INFO)
        handler.setFormatter(log_formatter)
        GM.logger.addHandler(handler)

        GM.logger.info("Application configs have been read successfully.")
        # Initialize system arguments.
        if sys.argv:
            for item in sys.argv:
                # Enable safe mode.
                if item == "-safe":
                    GM.safe_mode = True
                    print('Safe mode has been enabled.')
                    GM.logger.info("Safe mode has been enabled through system arguments.")
                if item == "-debug":
                    GM.debug_mode = True
                    print('Debug mode has been enabled.')
                    GM.logger.info("Debug mode has been enabled through system arguments.")
                if item == "-quiet":
                    GM.quiet_mode = True
                    print('Quiet mode has been enabled.')
                    GM.logger.info("Quiet mode has been enabled through system arguments.")
                if item == "-verbose":
                    GM.verbose_mode = True
                    print('Verbose mode has been enabled.')
                    GM.logger.info("Verbose mode has been enabled through system arguments.")
        # Initialize command queue.
        self.command_queue = QueueHandler(25)
        # Run Debug Mode tests.
        if GM.debug_mode:
            self.config_debug()
        # Retrieve mumble client data from configs.
        server_ip = GM.cfg['Connection_Settings']['ServerIP']
        server_pass = GM.cfg['Connection_Settings']['ServerPassword']
        server_port = int(GM.cfg['Connection_Settings']['ServerPort'])
        user_id = GM.cfg['Connection_Settings']['UserID']
        user_cert = GM.cfg['Connection_Settings']['UserCertification']
        auto_reconnect = GM.cfg.getboolean('Connection_Settings', 'AutoReconnect', fallback=False)
        GM.logger.info("Retrieved server information from application configs.")
        # Set main logic loop tick rate.
        self.tick_rate = float(GM.cfg['Main_Settings']['TickRate'])
        # Set multi-command limit.
        self.multi_cmd_limit = int(GM.cfg['Main_Settings']['MultiCommandLimit'])
        # Set the command token.
        self.cmd_token = GM.cfg['Main_Settings']['CommandToken']
        if len(self.cmd_token) != 1:
            print("ERROR: The command token must be a single character! Reverting to the default: '!' token.")
            GM.logger.critical("ERROR: The command token must be a single character! Reverting to the default: '!' token.")
            self.cmd_token = '!'
        # Initialize mumble client.
        self.mumble = pymumble.Mumble(server_ip, user=user_id, port=server_port, certfile=user_cert,
                                      password=server_pass, reconnect=auto_reconnect)
        # Initialize mumble callbacks.
        self.mumble.callbacks.set_callback("text_received", self.message_received)
        # Set mumble codec profile.
        self.mumble.set_codec_profile("audio")
        # Create temporary directories.
        utils.make_directory(GM.cfg['Media_Directories']['TemporaryMediaDirectory'])
        utils.make_directory(GM.cfg['Media_Directories']['TemporaryImageDirectory'])
        GM.logger.info("Initialized temporary media directories.")
        # Setup privileges.
        pv.setup_privileges()
        GM.logger.info("Initialized user privileges.")
        # Setup aliases.
        aliases.setup_aliases()
        GM.logger.info("Initialized aliases.")
        # Initialize plugins.
        if GM.safe_mode:
            self.initialize_plugins_safe()
            GM.logger.info("Initialized plugins with safe mode.")
        else:
            self.initialize_plugins()
            GM.logger.info("Initialized plugins.")
        # Run a plugin callback test.
        self.plugin_callback_test()
        GM.logger.info("Plugin callback test successful.")
        print("JJ Mumble Bot initialized!\n")
        # Join the server after all initialization is complete.
        self.join_server()
        GM.logger.info("JJ Mumble Bot has fully initialized and joined the server.")
        self.loop()

    # Prints all the contents of the config.ini file.
    def config_debug(self):
        print("\n-------------------------------------------")
        print("Config Debug:")
        for sect in GM.cfg.sections():
            print("[%s]" % sect)
            for (key, val) in GM.cfg.items(sect):
                print("%s=%s" % (key, val))
        print("-------------------------------------------\n")

    # Initializes only safe-mode applicable plugins.
    def initialize_plugins_safe(self):
        # Load Plugins
        reg_print("\n######### Initializing Plugins #########\n")
        sys.path.insert(0, utils.get_plugin_dir())
        for p_file in os.listdir(utils.get_plugin_dir()):
            f_name, f_ext = os.path.splitext(p_file)
            if f_ext == ".py":
                if f_name == "help":
                    continue
                elif f_name == "bot_commands" or f_name == "uptime":
                    plugin = __import__(f_name)
                    self.bot_plugins[f_name] = plugin.Plugin()
        help_plugin = __import__('help')
        self.bot_plugins['help'] = help_plugin.Plugin(self.bot_plugins)
        sys.path.pop(0)
        reg_print("\n######### Plugins Initialized #########\n")

    # Initializes all available plugins.
    def initialize_plugins(self):
        reg_print("\n######### Initializing Plugins #########\n")
        sys.path.insert(0, utils.get_plugin_dir())
        for p_file in os.listdir(utils.get_plugin_dir()):
            f_name, f_ext = os.path.splitext(p_file)
            if f_ext == ".py":
                if f_name == "help" or f_name == "youtube":
                    continue
                else:
                    plugin = __import__(f_name)
                    self.bot_plugins[f_name] = plugin.Plugin()

        # Import the help and youtube plugins separately.
        help_plugin = __import__('help')
        youtube_plugin = __import__('youtube')
        # Assign audio plugins manually.
        self.bot_plugins['youtube'] = youtube_plugin.Plugin()
        self.bot_plugins.get('youtube').set_sound_board_plugin(self.bot_plugins.get('sound_board'))
        self.bot_plugins.get('sound_board').set_youtube_plugin(self.bot_plugins.get('youtube'))
        self.bot_plugins['help'] = help_plugin.Plugin(self.bot_plugins)
        sys.path.pop(0)
        reg_print("\n######### Plugins Initialized #########\n")

    # Runs a check to add any new plugins that have been detected at runtime.
    def live_plugin_check(self):
        if GM.safe_mode:
            length_check = 3
        else:
            length_check = len([f for f in os.listdir(utils.get_plugin_dir()) if os.path.isfile(os.path.join(utils.get_plugin_dir(), f))])
        if length_check != len(self.bot_plugins):
            reg_print("Plugin change detected... adding to plugin cache.")
            GM.logger.warning("Plugin change detected... adding to plugin cache.")
            self.refresh_plugins()

    # A callback test that prints out the test outputs of all the registered plugins.
    def plugin_callback_test(self):
        # Plugin Callback Tests
        reg_print("\n######### Running plugin callback tests #########\n")
        for plugin in self.bot_plugins.values():
            plugin.plugin_test()
        reg_print("\n######### Plugin callback tests complete #########\n")

    # Refreshes all active plugins by quitting out of them completely and restarting them.
    def refresh_plugins(self):
        reg_print("Refreshing all plugins...")
        utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                   "%s is refreshing all plugins." % utils.get_bot_name())
        for plugin in self.bot_plugins.values():
            plugin.quit()
        self.bot_plugins.clear()
        if GM.safe_mode:
            self.initialize_plugins_safe()
        else:
            self.initialize_plugins()
        pv.setup_privileges()
        reg_print("All plugins refreshed.")
        utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                   "%s has refreshed all plugins." % utils.get_bot_name())
        GM.logger.info("JJ Mumble Bot has refreshed all plugins.")

    def join_server(self):
        self.mumble.start()
        self.mumble.is_ready()
        self.bot_status = "Online"
        self.mumble.users.myself.comment(
            "This is %s [%s].<br>%s<br>" % (utils.get_bot_name(), utils.get_version(), utils.get_known_bugs()))
        self.mumble.set_bandwidth(192000)
        self.mumble.channels.find_by_name(utils.get_default_channel()).move_in()
        utils.mute(self.mumble)
        self.mumble.channels[self.mumble.users.myself['channel_id']].send_text_message("%s is Online." % utils.get_bot_name())
        reg_print("\n\nJJMumbleBot is %s\n\n" % self.status())

    def status(self):
        return self.bot_status

    def message_received(self, text):
        message = text.message.strip()
        user = self.mumble.users[text.actor]
        if "<img" in message:
            reg_print("Message Received: [%s -> Image Data]" % user['name'])
        elif "<a href=" in message:
            reg_print("Message Received: [%s -> Hyperlink Data]" % user['name'])
        else:
            reg_print("Message Received: [%s -> %s]" % (user['name'], message))

        if message[0] == self.cmd_token:
            GM.logger.info("Commands Received: [%s -> %s]" % (user['name'], message))
            self.live_plugin_check()

            # example input: !version ; !about ; !yt twice ; !p ; !status
            all_commands = [msg.strip() for msg in message.split(';')]
            # example output: ["!version", "!about", "!yt twice", "!p", "!status"]

            if len(all_commands) > self.multi_cmd_limit:
                reg_print("The multi-command limit was reached! The multi-command limit is %d commands per line." % self.multi_cmd_limit)
                GM.logger.warning("The multi-command limit was reached! The multi-command limit is %d commands per line." % self.multi_cmd_limit)
                return

            # Iterate through all commands provided and generate commands.
            for i, item in enumerate(all_commands):
                # Generate command with parameters
                new_text = copy.deepcopy(text)
                new_text.message = item
                new_command = Command(item[1:].split()[0], new_text)

                if new_command.command in aliases.aliases:
                    alias_commands = [msg.strip() for msg in aliases.aliases[new_command.command].split('|')]
                    for x, xitem in enumerate(alias_commands):
                        new_xtext = copy.deepcopy(text)
                        new_xtext.message = xitem
                        new_xcommand = Command(xitem[1:].split()[0], new_xtext)
                        self.command_queue.insert(new_xcommand)
                else:
                    # Insert command into the command queue
                    self.command_queue.insert(new_command)

            # Process commands if the queue is not empty
            while not self.command_queue.is_empty():
                # Process commands in the queue
                cur_cmd = self.command_queue.pop()
                thr = threading.Thread(target=self.process_command_queue, args=(cur_cmd,))
                thr.start()
                if cur_cmd.command == "yt" or cur_cmd.command == "youtube":
                    thr.join()
                # self.process_command_queue(cur_cmd)
                time.sleep(self.tick_rate)

    def process_core_commands(self, command, text):
        if command == "alias":
            if pv.privileges_check(self.mumble.users[text.actor]) >= pv.Privileges.ADMIN.value:
                message = text.message.strip()
                message_parse = message[1:].split(' ', 2)
                alias_name = message_parse[1]

                if alias_name in aliases.aliases.keys():
                    aliases.set_alias(alias_name, message_parse[2])
                    debug_print("Registered alias: [%s] - [%s]" % (alias_name, message_parse[2]))
                    utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                               "Registered alias: [%s] - [%s]" % (alias_name, message_parse[2]))
                else:
                    aliases.add_to_aliases(alias_name, message_parse[2])
                    debug_print("Registered new alias: [%s] - [%s]" % (alias_name, message_parse[2]))
                    utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                               "Registered new alias: [%s] - [%s]" % (alias_name, message_parse[2]))
                return
            else:
                reg_print("User [%s] must be an admin to use this command." % (self.mumble.users[text.actor]['name']))
                GM.logger.warning(
                    "User [%s] tried to enter an admin-only command." % (self.mumble.users[text.actor]['name']))
            return

        elif command == "aliases":
            if pv.privileges_check(self.mumble.users[text.actor]) >= pv.Privileges.DEFAULT.value:
                cur_text = "<br><font color='red'>Registered Aliases:</font>"
                for i, alias in enumerate(aliases.aliases):
                    cur_text += "<br><font color='cyan'>[%s]</font><font color='yellow'> - [%s]</font>" % (alias, BeautifulSoup(aliases.aliases[alias], "html.parser").get_text())
                    if i % 50 == 0 and i != 0:
                        utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                                   '%s' % cur_text)
                        cur_text = ""
                utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                           '%s' % cur_text)
                return
            else:
                reg_print("User [%s] must not be blacklisted to use this command." % (self.mumble.users[text.actor]['name']))
                GM.logger.warning("User [%s] tried to enter an non-blacklisted command." % (self.mumble.users[text.actor]['name']))
            return

        elif command == "removealias":
            if pv.privileges_check(self.mumble.users[text.actor]) >= pv.Privileges.ADMIN.value:
                message = text.message.strip()
                message_parse = message[1:].split(' ', 2)
                alias_name = message_parse[1]
                if aliases.remove_from_aliases(alias_name):
                    debug_print('Removed [%s] from registered aliases.' % alias_name)
                    utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                               'Removed [%s] from registered aliases.' % alias_name)
                else:
                    debug_print('Could not remove [%s] from registered aliases.' % alias_name)
                    utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                               'Could not remove [%s] from registered aliases.' % alias_name)
                return
            else:
                reg_print("User [%s] must not be blacklisted to use this command." % (self.mumble.users[text.actor]['name']))
                GM.logger.warning(
                    "User [%s] tried to enter an non-blacklisted command." % (self.mumble.users[text.actor]['name']))
            return

        elif command == "clearaliases":
            if pv.privileges_check(self.mumble.users[text.actor]) >= pv.Privileges.ADMIN.value:
                if aliases.clear_aliases():
                    debug_print('Cleared allr egistered aliases.')
                    utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                               'Cleared all registered aliases.')
                else:
                    debug_print('The registered aliases could not be cleared.')
                    utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                               'The registered aliases could not be cleared.')
                return
            else:
                reg_print("User [%s] must be an admin to use this command." % (self.mumble.users[text.actor]['name']))
                GM.logger.warning(
                    "User [%s] tried to enter an admin-only command." % (self.mumble.users[text.actor]['name']))
            return

        elif command == "refresh":
            if pv.privileges_check(self.mumble.users[text.actor]) >= pv.Privileges.ADMIN.value:
                self.refresh_plugins()
                return
            else:
                reg_print("User [%s] must be an admin to use this command." % (self.mumble.users[text.actor]['name']))
                GM.logger.warning("User [%s] tried to enter an admin-only command." % (self.mumble.users[text.actor]['name']))
            return
        elif command == "sleep":
            if pv.privileges_check(self.mumble.users[text.actor]) >= pv.Privileges.ADMIN.value:
                sleep_time = float(text.message[1:].split(' ', 1)[1].strip())
                self.tick_rate = sleep_time
                debug_print("Sleeping for %s seconds..." % sleep_time)
                time.sleep(sleep_time)
                self.tick_rate = float(GM.cfg['Main_Settings']['TickRate'])
                return
            else:
                reg_print("User [%s] must be an admin to use this command." % (self.mumble.users[text.actor]['name']))
                GM.logger.warning("User [%s] tried to enter an admin-only command." % (self.mumble.users[text.actor]['name']))
            return
        elif command == "exit" or command == "quit":
            if pv.privileges_check(self.mumble.users[text.actor]) >= pv.Privileges.ADMIN.value:
                debug_print("Stopping all threads...")
                self.exit()
                GM.logger.info("JJ Mumble Bot is being shut down.")
                return
            else:
                reg_print("User [%s] must be an admin to use this command." % (self.mumble.users[text.actor]['name']))
                GM.logger.warning("User [%s] tried to enter an admin-only command." % (self.mumble.users[text.actor]['name']))
            return
        elif command == "status":
            if pv.privileges_check(self.mumble.users[text.actor]) == pv.Privileges.BLACKLIST.value:
                reg_print("User [%s] must not be blacklisted to use this command." % (self.mumble.users[text.actor]['name']))
                return
            utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                       "%s is %s." % (utils.get_bot_name(), self.status()))
            return
        elif command == "version":
            if pv.privileges_check(self.mumble.users[text.actor]) == pv.Privileges.BLACKLIST.value:
                reg_print("User [%s] must not be blacklisted to use this command." % (self.mumble.users[text.actor]['name']))
                return
            utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                       "%s is on version %s" % (utils.get_bot_name(), utils.get_version()))
            return
        elif command == "system_test":
            if pv.privileges_check(self.mumble.users[text.actor]) >= pv.Privileges.ADMIN.value:
                self.plugin_callback_test()
                debug_print("A system self-test was run.")
                GM.logger.info("A system self-test was run.")
                return
            else:
                reg_print("User [%s] must be an admin to use the system_test command." % (self.mumble.users[text.actor]['name']))
                GM.logger.warning("User [%s] tried to enter an admin-only command." % (self.mumble.users[text.actor]['name']))
            return
        elif command == "about":
            if pv.privileges_check(self.mumble.users[text.actor]) == pv.Privileges.BLACKLIST.value:
                reg_print("User [%s] must not be blacklisted to use this command." % (self.mumble.users[text.actor]['name']))
                return
            utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                       "%s" % utils.get_about())
            return
        return

    def process_command_queue(self, com):
        command_type = com.command
        command_text = com.text
        self.process_core_commands(command_type, command_text)
        for plugin in self.bot_plugins.values():
            plugin.process_command(self.mumble, command_text)

    def exit(self):
        utils.echo(self.mumble.channels[self.mumble.users.myself['channel_id']],
                   "%s was manually disconnected." % utils.get_bot_name())
        for plugin in self.bot_plugins.values():
            plugin.quit()
        utils.clear_directory(utils.get_temporary_media_dir())
        utils.clear_directory(utils.get_temporary_img_dir())
        reg_print("Cleared temporary directories.")
        self.exit_flag = True
        
    def loop(self):
        while not self.exit_flag:
            time.sleep(self.tick_rate)
