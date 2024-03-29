#!/usr/bin/python3

# Import Python and local modules.
import os
import re
import time
from PIL import Image
import obs_manager as obs
from mail_sender import send_mail
from obs_manager_conf import BACKGROUND_DIR, RECORDING_PATH

# Import Kivy modules.
import kivy
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import Line, Color
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import ScreenManager, Screen

# Path to the scene thumbnails.
SCENE_RELPATH = "images/scenes/"

# Supported thumbnail image size.
THUMB_SIZE_X = 320; THUMB_SIZE_Y = 180

# Recording time in seconds.
OBS_REC_TIME = 60

# Time in idle after sent mail.
RESTART_TIME = 10

# Timeout for the OBS connection.
OBS_TIMEOUT = 45

# OBS handler object.
OBS_HANDLER = None

class WindowManager(ScreenManager):
    ''' Utility class for window transitions and management. '''
    pass

class SceneSelectWindow(Screen):
    def init_scene_status(self, widget):
        ''' Adds a box around the current active scene. '''

        # Get the active scene from OBS, without the file ending.
        try:
            activeSceneName = OBS_HANDLER.get_current_background().split(".")[0]
        except:
            print("OBS connection error: OBS not responding!")
            quit()

        # Search all avail. scenes in the stack.
        for button in widget.ids.stack.children:
            
            # Remove both the path and the file ending from the given thumbnail/scene image.
            sceneName = button.background_normal.replace(SCENE_RELPATH, "").split(".")[0]

            # Set a box around the active scene button.
            if sceneName == activeSceneName:
                widget.ids.stack.set_box(button)
                break
            
class SceneSelectStack(StackLayout):
    ''' Scene/background select stack. '''

    def __init__(self, **kw):
        super().__init__(**kw)

        self.buttons = list()

        # Get a list of scene thumbnail paths.
        scenes = os.listdir(SCENE_RELPATH)
        scenes.sort()

        # Canvas active scene box.
        self.activeBox = None
        
        # Add all thumbnails as buttons.
        for scene in scenes:
            thumbnail = "images/scenes/" + scene
            btn = Button(background_normal = thumbnail, background_down = thumbnail, size_hint = (None, None), width = "320dp", height = "180dp")
            btn.bind(on_press = self.callback)
            self.add_widget(btn)
            self.buttons.append(btn)

    def callback(self, button):
        ''' Callback for each of the scene buttons. '''

        # Get the name of the selected (clicked button) scene, without any file ending.
        sceneName = button.background_normal.replace(SCENE_RELPATH, "").split(".")[0]

        # List all avail. video backgrounds.
        backgrounds = os.listdir(BACKGROUND_DIR)

        # Set background video to the selected scene name.
        for video in backgrounds:
            if video.split(".")[0] == sceneName:
                try:
                    OBS_HANDLER.set_background(video)
                except:
                    print("OBS connection error: OBS not responding!")
                    quit()

        # Set a box around the new active scene button.
        self.set_box(button)

    def set_box(self, button):
        ''' Creates a yellow box around a button, removes prev. box. '''

        # Draw box/frame.
        with self.canvas:

            # Width and color of the box.
            setWidth = 3
            Color(196/255, 237/255, 14/255, 1)

            # Remove old/prev. box.
            if self.activeBox != None:
                self.canvas.remove(self.activeBox)
                self.activeBox = None

            # Add the the box/frame around the selected button, indicating a active scene.
            self.activeBox = Line(width = setWidth + 1, rectangle = (button.x + setWidth, button.y + setWidth, button.width - setWidth * 2, button.height - setWidth * 2))
            self.bind(size = self.update_box_on_resize)
    
    def update_box_on_resize(self, *largs):
        ''' Handle window re-sizing on active box. '''

        # Get the current active scene, exclude the file name.
        activeSceneName = OBS_HANDLER.get_current_background().split(".")[0]

        # Update the box positon by setting it around the current active scene.
        for button in self.buttons:
            if button.background_normal.replace(SCENE_RELPATH, "").split(".")[0] == activeSceneName:
                self.set_box(button)
                break

class EmailWindow(Screen):
    ''' Email window. '''
    def __init__(self, **kw):
        super().__init__(**kw)

        # Keyboard for email screen.
        self.keyboard = None

    def create_keyboard(self):
        ''' Create a new keyboard if it does not already exist. '''

        if self.keyboard == None:

            # Create a new virtual keyboard.
            self.keyboard = VKeyboard(
                on_key_up = self.key_press,
                layout = "emailKeyboard.json",
                pos_hint = {"center_x": 0.5, "center_y": 0.3}
            )

            # Add the keyboard widget.
            self.add_widget(self.keyboard)

    def key_press(self, keyboard, keycode, *largs):
        ''' Handle keyboard input. '''

        # Remove all text.
        if keycode == "clear":
            self.ids.mail.text = ""
            return

        # Remove one letter.
        if keycode == "backspace":
            self.ids.mail.text = self.ids.mail.text[0:len(self.ids.mail.text) - 1]
            return

        # Append letter to the text.
        self.ids.mail.text += keycode
        
    def on_input_error(self, *largs):
        ''' Help user to type a valid email address. '''

        # Display red text on unvalid input and green text on valid input.
        exp = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if re.fullmatch(exp, self.ids.mail.text):
            self.ids.mail.foreground_color = (0, 0.6, 0, 1)
        else:
            self.ids.mail.foreground_color = (0.8, 0, 0, 1)

    def clear_mail(self):
        ''' Remove field and reset on i.e. a cancel or enter. '''

        # Stop input helper, set default color and clear text.
        self.ids.mail.unbind(text = self.on_input_error)
        self.ids.mail.foreground_color = (0, 0, 0, 1)
        self.ids.mail.text = ""

    def set_mail(self):
        '''
        Set the global mail object if a valid address is entered,
        and proceed to the next screen afterwards (start recording).
        '''

        # Get app object, with globals.
        app = App.get_running_app()

        # Test that the provided email address is valid.
        exp = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if not re.fullmatch(exp, self.ids.mail.text):

            # Indicate user error by setting red color.
            self.ids.mail.foreground_color = (0.8, 0, 0, 1)

            # Activate user email address typing help.
            self.ids.mail.bind(text = self.on_input_error)

        else:
            
            # Valid input, set the current active mail.
            app.USER_MAIL = self.ids.mail.text

            # Switch to the recording screen.
            self.manager.current = "RECORD"

class RecordWindow(Screen):
    ''' Record window. '''

    def reset_progress_bar(self):
        ''' Progress (in seconds) should start at zero. '''
        self.ids.progress.value = 0

    def start_recording(self):
        ''' Schedules a recording with OBS. '''

        # Start OBS recording.
        try:
            OBS_HANDLER.start_recording()
        except:
            print("OBS connection error: OBS not responding!")
            quit()

        # Update the recording progress each second.
        Clock.schedule_interval(self.update_progress, 1)

    def update_progress(self, *largs):

        # Increment progress with one second.
        self.ids.progress.value += 1

        # Stop the recording after a set time has passed.
        if self.ids.progress.value >= OBS_REC_TIME:

            # Stop OBS recording.
            try:
                OBS_HANDLER.stop_recording()
            except:
                print("OBS connection error: OBS not responding!")
                quit()

            # Switch to the end screen.
            self.manager.current = "END"

            # Stop the clock schedule.
            return False

class EndWindow(Screen):
    ''' End/send video window. '''

    def send_video(self):
        ''' Send the recorded video with email. '''

        app = App.get_running_app()

        # Get path to recording to send.
        recFile = os.listdir(RECORDING_PATH)[0]
        recPath = RECORDING_PATH + "/" + recFile

        # Mail subject (NOR/ENG/GER).
        subject = {
            "NOR": "Din film fra Nordnorsk vitensenter",
            "ENG": "Your film from the Science Centre of Northern Norway",
            "GER": "Ihr Film vom Wissenschaftszentrum Nordnorwegen"
        }

        # Mail body (NOR/ENG/GER).
        body = {
            "NOR": "Her er værreportasjen du spilte inn på Nordnorsk vitensenter.",
            "ENG": "Here is the weather report you recorded at the Science Centre of Northern Norway.",
            "GER": "Hier ist der Wetterbericht, den Sie im Wissenschaftszentrum Nordnorwegens aufgezeichnet haben."
        }

        # Attempt to send the mail to the user, use set language for subject and body.
        if send_mail(app.USER_MAIL, subject[app.LANGUAGE], body[app.LANGUAGE], recPath):
            # Display OK response.
            if app.LANGUAGE == "NOR":
                self.ids.sentHint.text = "OPPTAK SENDT"
            elif app.LANGUAGE == "ENG":
                self.ids.sentHint.text = "RECORDING SENT"
            elif app.LANGUAGE == "GER":
                self.ids.sentHint.text = "AUFZEICHNUNG GESENDET"
        else:
            # Display ERROR response.
            if app.LANGUAGE == "NOR":
                self.ids.sentHint.text = "SENDING FEILET"
            elif app.LANGUAGE == "ENG":
                self.ids.sentHint.text = "FAILED TO SEND"
            elif app.LANGUAGE == "GER":
                self.ids.sentHint.text = "SENDEN FEHLGESCHLAGEN"

        # Restart OBS studio.
        try:
            OBS_HANDLER.restart(OBS_TIMEOUT)
        except:
            print("OBS connection error: OBS not responding!")
            quit()
        
        # Wait, before restarting.
        Clock.schedule_once(self.go_to_start_screen)

    def go_to_start_screen(self, *largs):
        ''' Go back to the start screen, after a given sleep time. '''
        time.sleep(RESTART_TIME)
        self.manager.current = "LANG-SELECT"

    def reset(self):
        ''' Reset state for the next user. '''

        app = App.get_running_app()

        # Clear active mail.
        app.USER_MAIL = ""

        # Set default language.
        app.LANGUAGE = "ENG"

def setup():
    ''' Setup utility function, called once. '''

    kivy.require("2.1.0")

    # Get lists of background image/thumbnail names and background video names, without file endings.
    backgroundVideos = list(map(lambda file: file.split(".")[0], os.listdir(BACKGROUND_DIR)))
    backgroundImages = list(map(lambda file: file.split(".")[0], os.listdir(SCENE_RELPATH)))

    # Dulicate image files (with i.e. different endings) are not allowed.
    if len(backgroundImages) != len(set(backgroundImages)):
        print(f"Error: Duplicate thumbnails in {SCENE_RELPATH} exists!")
        quit()

    # Dulicate video files (with i.e. different endings) are not allowed.
    if len(backgroundVideos) != len(set(backgroundVideos)):
        print(f"Error: Duplicate background videos in {BACKGROUND_DIR} exists!")
        quit()

    # All background videos must have a unique thumbnail.
    for videoName in backgroundVideos:
        if videoName not in backgroundImages:
            print(f"Error: Thumbnail in '{SCENE_RELPATH}' for background '{videoName}' in '{SCENE_RELPATH}' does not exist!")
            quit()

    # Confirm that only valid background images exist.
    for image in os.listdir(SCENE_RELPATH):

        # Get image dimensions, i.e. the width and height.
        imgSizeX, imgSizeY = Image.open(SCENE_RELPATH + image).size

        # Print warning upon wrong image dimensions.
        if imgSizeX != THUMB_SIZE_X and imgSizeY != THUMB_SIZE_Y:
            print(f"Warning: Thumbnail with name '{image}' does not match the req. 320x180 size, it is {imgSizeX}x{imgSizeY}.")

    # Connect to OBS.
    global OBS_HANDLER
    OBS_HANDLER = obs.obs_manager(OBS_TIMEOUT)
    if OBS_HANDLER == None:
        print("OBS connection failed: Check OBS websocket settings!")
        quit()

    # Config. kivy screen settings.
    Window.size = (1100, 800)
    Window.minimum_width, Window.minimum_height = Window.size
    Window.clearcolor = (0.1, 0.1, 0.1, 1)
    Window.borderless = True
    Window.maximize()
    
class WeatherReportStationApp(App):
    ''' Kivy Weather Report Station UI app.'''

    # Set title of the UI window.
    title = "Weather Report Station"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Current UI language.
        self.LANGUAGE = "ENG"

        # Current active user mail address.
        self.USER_MAIL = str()

    def build(self):
        return super().build()

    def set_language(self, code):
        '''
        Selects a language, but does not change any text.
        Call set_language, and then set_strings before displaying
        the content to alter user text to the correct language.
        
        Valid language codes: "NOR", "ENG" and "GER", as strings.
        '''
        self.LANGUAGE = code

    def set_strings(self, widget):
        '''
        Sets all text to the specified/selected language.
        All user text labels should be declared in this method.

        Hint: this method must be called within the correct screen.
        Use "on_pre_enter" in the "kv" file to set upcoming content.
        '''

        # Norwegian user text.
        if self.LANGUAGE == "NOR":
            if str(widget) == "<Screen name='SCENE'>":
                widget.ids.selectScene.text = "Velg en bakgrunn:"
                widget.ids.exitButton.text = "AVBRYT"
                widget.ids.contButton.text = "FORTSETT TIL OPPTAK"

            if str(widget) == "<Screen name='MAIL'>":
                widget.ids.mailHeader.text = "Skriv inn din e-post addresse:"
                widget.ids.mail.hint_text = "brukernavn@mail.no"
                widget.ids.info.text = "Opptaket blir sendt til den angitte adressen.\nSendingen varer i 60 sekunder."
                widget.ids.exitButton.text = "TILBAKE"
                widget.ids.contButton.text = "START OPPTAK"

            if str(widget) == "<Screen name='RECORD'>":
                widget.ids.recording.text = "OPPTAK PÅGÅR"

            if str(widget) == "<Screen name='END'>":
                widget.ids.sentHint.text = "SENDER OPPTAKET"

        # English user text.
        elif self.LANGUAGE == "ENG":
            if str(widget) == "<Screen name='SCENE'>":
                widget.ids.selectScene.text = "Select a background:"
                widget.ids.exitButton.text = "CANCEL"
                widget.ids.contButton.text = "CONTINUE TO RECORDING"

            if str(widget) == "<Screen name='MAIL'>":
                widget.ids.mailHeader.text = "Enter your e-mail address:"
                widget.ids.mail.hint_text = "username@mail.com"
                widget.ids.info.text = "The recording will be sent to the given address.\nThe broadcast lasts for 60 seconds."
                widget.ids.exitButton.text = "RETURN"
                widget.ids.contButton.text = "START RECORDING"

            if str(widget) == "<Screen name='RECORD'>":
                widget.ids.recording.text = "RECORDING IN PROGRESS"

            if str(widget) == "<Screen name='END'>":
                widget.ids.sentHint.text = "SENDING THE RECORDING"

        # German user text.
        elif self.LANGUAGE == "GER":
            if str(widget) == "<Screen name='SCENE'>":
                widget.ids.selectScene.text = "Wählen Sie einen Hintergrund:"
                widget.ids.exitButton.text = "ABBRECHEN"
                widget.ids.contButton.text = "MIT AUFZEICHNUNG FORTFAHREN"
            
            if str(widget) == "<Screen name='MAIL'>":
                widget.ids.mailHeader.text = "Geben Sie Ihre E-Mail-Adresse ein:"
                widget.ids.mail.hint_text = "benutzername@mail.com"
                widget.ids.info.text = "Die Aufzeichnung wird an die angegebene Adresse gesendet.\nDie Übertragung dauert 60 Sekunden."
                widget.ids.exitButton.text = "ZURÜCK"
                widget.ids.contButton.text = "AUFNAHME BEGINNEN"

            if str(widget) == "<Screen name='RECORD'>":
                widget.ids.recording.text = "AUFNAHME LAUFT"

            if str(widget) == "<Screen name='END'>":
                widget.ids.sentHint.text = "AUFZEICHNUNG WIRD GESENDET"
        
if __name__ == "__main__":
    ''' Run the main application. '''

    try:
        setup()
        WeatherReportStationApp().run()
    except KeyboardInterrupt:
        quit()
    finally:
        OBS_HANDLER.obs_process.__del__()
