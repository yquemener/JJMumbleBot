from JJMumbleBot.lib.utils import dir_utils
from JJMumbleBot.settings import global_settings
from JJMumbleBot.lib.utils.print_utils import dprint, rprint
from JJMumbleBot.plugins.extensions.text_to_speech.resources.strings import *
from JJMumbleBot.plugins.extensions.text_to_speech.utility import settings
from JJMumbleBot.lib.resources.strings import *
from JJMumbleBot.lib.resources.strings import C_PLUGIN_SETTINGS
from JJMumbleBot.lib.utils import runtime_utils
import os
import wave
import time
import audioop
import subprocess as sp
import requests
import json


def prepare_tts_list():
    file_counter = 0
    gather_list = []
    for file_item in os.listdir(f"{dir_utils.get_perm_med_dir()}/text_to_speech/"):
        if file_item.endswith(".oga"):
            if file_item.startswith("_temp"):
                continue
            gather_list.append(f"{file_item}")
            file_counter += 1

    gather_list.sort(key=str.lower)
    return gather_list


def stop_audio():
    if global_settings.audio_inst is not None and settings.is_playing:
        dprint("Stopping text_to_speech audio thread...")
        global_settings.audio_inst.terminate()
        global_settings.audio_inst.kill()
        global_settings.audio_inst = None
        global_settings.audio_dni = (False, None)
        settings.current_track = None
        return True
    return False


def get_cur_audio_length():
    wav_file = wave.open(f"{dir_utils.get_perm_med_dir()}/text_to_speech/{settings.current_track}.oga", 'r')
    frames = wav_file.getnframes()
    rate = wav_file.getframerate()
    duration = frames / float(rate)
    wav_file.close()
    return duration


def download_clip(clip_name, voice, msg, directory=None):
    temp = {'text': msg, 'voice': voice}
    json_dump = json.dumps(temp)

    if directory is None:
        directory = f'{dir_utils.get_perm_med_dir()}'

    try:
        url = 'https://streamlabs.com/polly/speak'
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        r = requests.post(url, data=json_dump, headers=headers)
        # print(r.status_code)
        if r.status_code == 200:
            resp = requests.get(json.loads(r.text)['speak_url'])
            # print(resp.status_code)
            if resp.status_code == 200:
                with open(f'{directory}/text_to_speech/{clip_name}.oga', 'wb') as f:
                    f.write(resp.content)
                uri = f'{directory}/text_to_speech/{clip_name}.oga'
                sp.call(
                    [settings.tts_metadata[C_PLUGIN_SETTINGS][P_VLC_DIR], uri] + ['-I', 'dummy', '--quiet',
                                                                         '--one-instance', '--no-repeat',
                                                                         '--sout',
                                                                         '#transcode{acodec=wav, channels=2, samplerate=43000, '
                                                                         'ab=192, threads=8}:std{access=file, mux=wav, '
                                                                         f'dst={directory}/text_to_speech/{clip_name}.wav '
                                                                         '}',
                                                                         'vlc://quit'])
                return True
            dprint(f'Could not download clip: Response-{r.status_code}')
            return False
        dprint(f'Could not download clip: Response-{r.status_code}')
        return False
    except Exception as e:
        dprint(e)
        return False


def clear_audio_thread():
    if global_settings.audio_inst is not None:
        dprint("Clearing text_to_speech audio thread...")
        global_settings.audio_inst.terminate()
        global_settings.audio_inst.kill()
        global_settings.audio_inst = None
        global_settings.audio_dni = (False, None)
        return True
    return False


def play_audio(mode=1):
    global_settings.audio_dni = (True, settings.tts_metadata[C_PLUGIN_INFO][P_PLUGIN_NAME])
    global_settings.mumble_inst.sound_output.clear_buffer()

    if mode == 0:
        uri = f"file:///{dir_utils.get_temp_med_dir()}/text_to_speech/{settings.current_track}.oga"
    else:
        uri = f"file:///{dir_utils.get_perm_med_dir()}/text_to_speech/{settings.current_track}.oga"

    command = settings.tts_metadata[C_PLUGIN_SETTINGS][P_VLC_DIR]

    if global_settings.audio_inst is not None:
        global_settings.audio_inst.terminate()
        global_settings.audio_inst.kill()
        global_settings.audio_inst = None

    settings.is_playing = True
    if global_settings.audio_inst is None:
        use_stereo = global_settings.cfg.getboolean(C_MAIN_SETTINGS, P_AUD_STEREO)
        if use_stereo:
            global_settings.audio_inst = sp.Popen(
                [command, uri] + ['-I', 'dummy', '--quiet', '--one-instance', '--no-repeat', '--sout',
                                  '#transcode{acodec=s16le, channels=2, samplerate=48000, '
                                  'ab=128, threads=8}:std{access=file, mux=wav, dst=-}',
                                  'vlc://quit'],
                stdout=sp.PIPE, bufsize=480)
        else:
            global_settings.audio_inst = sp.Popen(
                [command, uri] + ['-I', 'dummy', '--quiet', '--one-instance', '--no-repeat', '--sout',
                                  '#transcode{acodec=s16le, channels=2, samplerate=24000, '
                                  'ab=128, threads=8}:std{access=file, mux=wav, dst=-}',
                                  'vlc://quit'],
                stdout=sp.PIPE, bufsize=480)

    runtime_utils.unmute()
    while not settings.exit_flag and global_settings.audio_inst and settings.is_playing:
        while global_settings.mumble_inst.sound_output.get_buffer_size() > 0.5 and not settings.exit_flag:
            time.sleep(0.01)
        if global_settings.audio_inst:
            raw_music = global_settings.audio_inst.stdout.read(480)
            if raw_music and global_settings.audio_inst:
                global_settings.mumble_inst.sound_output.add_sound(audioop.mul(raw_music, 2, settings.volume))
            else:
                stop_audio()
                settings.is_playing = False
                return
        else:
            return
    return