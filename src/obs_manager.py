#!/usr/bin/python3

import time
import obsws_python
import subprocess
import os
import shutil
import obs_manager_conf as conf

class flatpak():
    '''
    Utility for managing flatpak applications.
    '''
    
    def __init__(self, app: str):
        '''
        Start a given flatpak application with flatpak run.
        '''
        self.app = app
        self.process = subprocess.Popen(['/bin/flatpak', 'run', self.app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def restart(self):
        '''
        Restarts the flatpak application using flatpak kill and flatpak run.
        '''
        subprocess.Popen(['/bin/flatpak', 'kill', self.app])
        self.process = subprocess.Popen(['/bin/flatpak', 'run', self.app])

    def __del__(self):
        '''
        When the flatpak object goes out of scope. Kill the flatpak process.
        '''
        subprocess.Popen(['/bin/flatpak', 'kill', self.app])

class obs_manager():
    '''
    Utility for managing OBS.
    '''
    def __init__(self, timeout):
        self.prepare()
        self.obs_process = flatpak('com.obsproject.Studio')
        self.connect_to_obs(timeout)
        self.setup()

    def prepare(self):
        '''
        Done before starting OBS.
        Resets scene_collection and profile.
        '''

        if os.path.exists(conf.scene_destination()):
            os.remove(conf.scene_destination())

        if os.path.exists(conf.OBS_SCENE_COLLECTION_SRC):
            shutil.copy(conf.OBS_SCENE_COLLECTION_SRC, conf.scene_destination())
        else:
            print(f"ERROR: Cant find {conf.OBS_SCENE_COLLECTION_SRC}")
            quit()

        if os.path.exists(conf.profile_destination_path()):
            shutil.rmtree(conf.profile_destination_path())

        if os.path.exists(conf.OBS_PROFILE_SRC):
            shutil.copytree(conf.OBS_PROFILE_SRC, conf.profile_destination_path())    
        else:
            print(f"ERROR: Can't find {conf.OBS_PROFILE_SRC}")
            quit()

    def setup(self):
        '''
        Done after starting OBS.
        Sets and configures active scene collection and profile.
        '''

        if conf.OBS_SCENE_COLLECTION_NAME in self.get_scene_collections():
            self.conn.set_current_scene_collection(conf.OBS_SCENE_COLLECTION_NAME)

        if conf.OBS_PROFILE_NAME in self.get_profiles():
            self.conn.set_current_profile(conf.OBS_PROFILE_NAME)

        if os.path.exists(os.path.abspath(conf.RECORDING_PATH)):
            self.conn.set_profile_parameter("AdvOut", "RecFilePath", os.path.abspath(conf.RECORDING_PATH))
        else:
            print(f"Could not find recording path: {os.path.abspath(conf.RECORDING_PATH)}")
            quit()

    def connect_to_obs(self, timeout):
        '''
        Connects to OBS using credentials from the config. file.
        '''

        # Get time in seconds.
        start_time = time.time()

        while(True):
            current_time = time.time()

            if current_time - start_time >= timeout:
                break

            try:
                self.conn = obsws_python.ReqClient(host = conf.HOST, port = conf.PORT, password = conf.PASSWORD)
                break
            except KeyboardInterrupt:
                exit()
            except:
                pass

        # This is done to deliberately cause an Exception if it failed to connect.
        print(f"OBS version: {self.conn.get_version()}")

    def get_scene_collections(self):
        return self.conn.get_scene_collection_list().scene_collections

    def get_profiles(self):
        return self.conn.get_profile_list().profiles

    def get_monitors(self):
        return self.conn.get_monitor_list().monitors
    
    def is_recording(self):
        return self.conn.get_record_status().output_active

    def start_recording(self):
        self.conn.start_record()

    def stop_recording(self):
        while(True):
            try:
                self.conn.stop_record()
                break
            except KeyboardInterrupt:       
                exit()
            except:
                pass

        while(self.is_recording()):
            pass

    def set_background(self, filename: str):
        if filename[0] == '/':
            settings = {
                'local_file': filename,
                'looping': True
            }
        else:
            settings = {
                'local_file': os.path.abspath(conf.BACKGROUND_DIR + '/' + filename),
                'looping': True
            }

        self.conn.set_input_settings(conf.OBS_BACKGROUND_SOURCE_NAME, settings, True)

    def get_current_background(self) -> str:
        return self.conn.get_input_settings(conf.OBS_BACKGROUND_SOURCE_NAME).input_settings['local_file'].split('/')[-1]

    def restart_background(self):
        '''
        Source: https://github.com/dnaka91/obws/blob/main/src/common.rs
        # OBS_WEBSOCKET_MEDIA_INPUT_ACTION_NONE #
        # OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY #
        # OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PAUSE #
        # OBS_WEBSOCKET_MEDIA_INPUT_ACTION_STOP #
        # OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART #
        # OBS_WEBSOCKET_MEDIA_INPUT_ACTION_NEXT #
        # OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PREVIOUS #
        '''
        obs.conn.trigger_media_input_action(conf.OBS_BACKGROUND_SOURCE_NAME, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART")

    def get_background_cursor(self):
        return self.conn.get_media_input_status(conf.OBS_BACKGROUND_SOURCE_NAME).media_cursor

if __name__ == "__main__":
    ''' Run simple demo. '''

    obs = obs_manager(100)

    while(True):
        try:
            cmd = input("COMMAND:")
            if cmd == "quit":
                quit()

        except KeyboardInterrupt:        
            exit()
