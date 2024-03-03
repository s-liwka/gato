import kivy
import sys
import subprocess
from threading import Thread, Event
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.lang import Builder
from kivy.clock import Clock
import time
from cryptography.fernet import Fernet
import modules.token_tools
from multiprocessing import Process, Queue


import json
import os

import modules.paths

import bot


Builder.load_file('app.kv')


class Tab(TabbedPanel):

    def __init__(self, **kwargs):
        super(Tab, self).__init__(**kwargs)
        self.queue = Queue()
        self.update_console_thread = Thread(target=self.update_console)
        self.update_console_thread.daemon = True
        self.update_console_thread.start()
        self.config = self.load_config()

        if 'logger' in self.config:
            self.ids.msglgrcb.active = self.config['logger']
        if 'sniper' in self.config:
            self.ids.sncb.active = self.config['sniper']
        if 'prefix' in self.config:
            self.ids.prti.text = self.config['prefix']
        if 'token' in self.config:
            self.ids.tkti.text = self.config['token']


    # config

    def load_config(self):
        self.config_file, self.config_dir = modules.paths.get_config_file_dir()
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

            return self.config

    def save_config(self):
         # check if already encrypted
        try:
            decrypted_token = modules.token_tools.decrypt_token(self.ids.tkti.text.encode('utf-8'))
            encrypted_token = self.ids.tkti.text.encode('utf-8')
            print('is encrypted')
        except: # will raise an exception when not
            decrypted_token = self.ids.tkti.text.encode('utf-8')
            encrypted_token = modules.token_tools.encrypt_token(self.ids.tkti.text.encode('utf-8'))
            print('not encrypted')

        decrypted_token = decrypted_token.replace('"', '')

        token_check = modules.token_tools.validate(decrypted_token)
        
        if token_check == 'invalid':
            content_layout = BoxLayout(orientation='vertical')
            content_layout.add_widget(Label(text='The token is invalid.'))
            ok_button = Button(text='OK')
            ok_button.bind(on_release=lambda x: popup.dismiss())
            content_layout.add_widget(ok_button)
            
            popup = Popup(title='Token Validation',
                        content=content_layout,
                        size_hint=(None, None), size=(400, 400))
            popup.open()

        elif token_check == 'err':
            content_layout = BoxLayout(orientation='vertical')
            content_layout.add_widget(Label(text='An error occurred while checking the token.'))
            ok_button = Button(text='OK')
            ok_button.bind(on_release=lambda x: popup.dismiss())
            content_layout.add_widget(ok_button)
            
            popup = Popup(title='Token Validation',
                        content=content_layout,
                        size_hint=(None, None), size=(400, 400))
            popup.open()
                
        self.config = {
            'logger': self.ids.msglgrcb.active,
            'sniper': self.ids.sncb.active,
            'prefix': self.ids.prti.text,
            'token': encrypted_token.decode('utf-8'),
        }

        with open(self.config_file, 'w') as f:
            f.write(json.dumps(self.config))

        self.restart_bot()



    # bot
    
    def start_bot(self):
        self.config = self.load_config()
        self.ids.console.text = "[INFO] Starting selfbot...\n"
        self.ids.console.text += "[INFO] Validating token...\n"

        token = modules.token_tools.decrypt_token(self.config['token'])
        check_token = modules.token_tools.validate(token)
        if check_token == 'invalid':
            self.ids.console.text += "[ERR] Invalid token."
            return
        elif check_token == 'err':
            self.ids.console.text += "[WARN] An error has occured while validating the token. Continuing...\n"
        else:
            self.ids.console.text += "[SUCCESS] Valid token."

        self.queue = Queue()
        self.bot_process = Process(target=bot.main, args=(token, self.queue))
        self.bot_process.daemon = True
        self.bot_process.start()

    def stop_bot(self):
        if hasattr(self, 'bot_process') and self.bot_process.is_alive():
            self.ids.console.text += "\n[INFO] Killing the bot...\n"
            self.bot_process.kill()
            self.bot_process.join()
            self.ids.console.text += "[SUCCESS] Killed the bot.\n"
        else:
            self.ids.console.text += "[INFO] Bot isn't on.\n"


    def restart_bot(self):
        self.stop_bot()
        self.start_bot()
    


    # console updater

    def update_console(self):
        i = 0
        while True:
            if not self.queue.empty():
                i += 1
                message = self.queue.get()
                print(message)
                self.ids.console.text += "\n" + message
                # I couldnt find a better way
                if i > 13:
                    self.ids.console.size_hint_y += 0.05
            time.sleep(0.1)
    

class MyApp(App):
    def build(self):
        self.title = "Sliwka's selfbot"
        return Tab()



if __name__ == '__main__':
    MyApp().run()