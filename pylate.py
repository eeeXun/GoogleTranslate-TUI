#!/usr/bin/python3
import npyscreen
import curses
import json
import requests
from urllib.parse import quote
from urllib.request import urlopen
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
from pygame import mixer
import time

readme = '''
        █▀▀ █▀█ █▀█ █▀▀ █░░ █▀▀ ▄▄ ▀█▀ █▀█ ▄▀█ █▄░█ █▀ █░░ ▄▀█ ▀█▀ █▀▀   ▀█▀ █░█ █
        █▄█ █▄█ █▄█ █▄█ █▄▄ ██▄ ░░ ░█░ █▀▄ █▀█ █░▀█ ▄█ █▄▄ █▀█ ░█░ ██▄   ░█░ █▄█ █

        This is an unofficial Google Translate client.
        It use Google Translate's API(free), so it may not work when you send too many requests.

        It just a practice for npyscreen, this respository may not update any more.

        - General
        -    ^Q           :         Quit
        -    ALT + ENTER  :         Search
        -    CTRL + T     :         Swap language
        -    CTRL + D     :         Delete all input
        -    CTRL + S     :         Select Language
        -
        - Sound
        -    CTRL + K     :         Play left sound
        -    CTRL + L     :         Play right sound
'''

CONFIG_DIR = os.getenv("HOME") + "/.config/pylate/"
with open(CONFIG_DIR + "config.json") as fp:
    config = json.load(fp)

class EditBox(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLineEdit

class SelectBox(npyscreen.BoxTitle):
    _contained_widget = npyscreen.SelectOne

class Sound:
    def __init__(self):
        self.url = "https://translate.google.com.vn/translate_tts?ie=UTF-8&q={}&tl={}&client=tw-ob"
        self.cache_file = "/tmp/translate.mp3"
        mixer.init()

    def play(self, message, language):
        source = urlopen(self.url.format(quote(message), language))

        # write to file
        with open(self.cache_file, "wb") as fp:
            fp.write(source.read())

        # play sound
        mixer.music.load(self.cache_file)
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.1)

class LanguageForm(npyscreen.ActionForm):
    def create(self):
        # get language list
        languages = list(self.parentApp.translator.languageCode.keys())
        codes = list(self.parentApp.translator.languageCode.values())

        # get terminal's size
        y, x = self.useable_space()

        inputDefault = languages.index(self.parentApp.translator.inputLanguage)
        outputDefault = languages.index(self.parentApp.translator.outputLanguage)

        self.input = self.add(SelectBox, name="Input Language",
            value=inputDefault,
            values=languages,
            max_height=y-5, max_width = x//2-5,
            relx=3, rely=3,
        )

        self.output = self.add(SelectBox, name="Output Language",
            value=outputDefault,
            values=languages,
            max_height=y-5, max_width = x//2-5,
            relx=x//2+3, rely=3,
        )

    def resize(self):
        # get terminal's size
        y, x = self.useable_space()

        self.input.max_height = y-5
        self.input_max_width = x//2-5

        self.output.max_height = y-5
        self.output.max_width = x//2-5
        self.output.relx = x//2+3
        self.output.entry_widget.relx = x//2+4

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self):
        languages = list(self.parentApp.translator.languageCode.keys())
        codes = list(self.parentApp.translator.languageCode.values())
        self.parentApp.translator.fr = codes[self.input.value[0]]
        self.parentApp.translator.to = codes[self.output.value[0]]
        self.parentApp.translator.inputLanguage = languages[self.input.value[0]]
        self.parentApp.translator.outputLanguage = languages[self.output.value[0]]
        self.parentApp.setNextForm("MAIN")

class MainForm(npyscreen.FormBaseNew):

    def while_waiting(self):
        if not self.lock:
            self.DISPLAY()
        else:
            self.lock = True

    def create(self):
        self.keypress_timeout = 5

        # lock is for INPUT's DISPLAY() updatting
        self.lock = False

        def inputUpdate():
            self.lock = False

        # set event handler
        event_handlers = {
            # send request
            curses.ascii.alt(curses.ascii.NL): self.send_text,

            #exit
            "^Q": self.exit_app,

            # delete all input
            "^D": self.remove_text,

            # select language
            "^S": self.change_language,

            # play sound on the left window
            "^K": self.play_left,

            # play sound on the right window
            "^L": self.play_right,

            # reverse language
            "^T": self.reverse_language
        }
        self.add_handlers(event_handlers)

        # get terminal's size
        y, x = self.useable_space()

        self.input = self.add(EditBox, name="Input (from)", footer=self.parentApp.translator.inputLanguage,
            max_width=x//2-5, max_height=y//3,
            relx=3, rely=3,
            value="Hello world"
        )

        # avoid some language input error
        # ex. Chinese
        self.input.entry_widget.when_value_edited = inputUpdate

        self.output = self.add(EditBox, name="Output (to)", footer=self.parentApp.translator.outputLanguage,
            max_width=x//2-5, max_height=y//3,
            relx=x//2+2, rely=3,
            value="你好，世界",
            editable=False
        )

        self.readme = self.add(EditBox, name="README",
            max_width=x-5, max_height=y//3*2-6,
            relx=3, rely=y//3+4,
            value=readme,
            editable=False
        )

    def resize(self):
        '''
            resize the form when the terminal is resizing
            This function will be called by npyscreen automatically.
        '''
        # get terminal's size
        y, x = self.useable_space()

        # change input's size
        self.input.max_width = x//2-5
        self.input.max_height = y//3

        # change output's size & location
        self.output.max_width = x//2-5
        self.output.max_height = y//3

        self.output.relx = x//2+2  # location(x)

        # change README's size & location
        self.readme.max_width = x-5
        self.readme.max_height = y//3*2-6
        self.readme.rely = y//3+4

        # Output and README's contained widget, TextField must be move to a new position
        self.output.entry_widget.relx = x//2+3
        self.readme.entry_widget.rely = y//3+5

        self.input.footer = self.parentApp.translator.inputLanguage
        self.output.footer = self.parentApp.translator.outputLanguage

    def send_text(self, event):
        '''
            use self.translator to send the request to Google Translate
            then update the response to self.output
        '''
        # When press ALT + ENTER, send request & update output's text
        if self.input.value != "":
            try:
                targetText = self.parentApp.translator.translate(self.input.value.replace('\n', ' '))
            except:
                targetText = ["This is not a true translation, there exist an error."]

            finally:
                text = ""
                for i in targetText:
                    text = text + i + "\n"
                self.output.value = text

                # refresh entire form
                # Though npyscreen's documentation mention that we should avoid using DISPLAY() function
                # I can't display Chinese or Japanese,etc correctly when I didn't use this function.
                self.DISPLAY()

    def play_left(self, event):
        if self.input.value != "":
            message = self.input.value
            language = self.parentApp.translator.fr
            Sound().play(message, language)

    def play_right(self, event):
        if self.output.value != "":
            message = self.output.value
            language = self.parentApp.translator.to
            Sound().play(message, language)

    def reverse_language(self, event):

        translator = self.parentApp.translator

        translator.to, translator.fr = translator.fr, translator.to
        translator.inputLanguage, translator.outputLanguage = translator.outputLanguage, translator.inputLanguage

        self.input.value, self.output.value = self.output.value, self.input.value

        self.input.footer = translator.inputLanguage
        self.input.update()

        self.output.footer = translator.outputLanguage
        self.output.update()

    def remove_text(self, event):
        self.input.value = ""
        self.input.update()

    def exit_app(self, event):
        exit(0)

    def change_language(self, event):
        self.parentApp.switchForm("LANGUAGE")

class GoogleTranslator():
    def __init__(self, fr, to):
        # set up
        self.languageCode = {}
        self.fr = fr
        self.to = to
        self.inputLanguage = ""
        self.outputLanguage = ""

        self.loadLanguageCode()

        self.URL = "https://translate.google.com.tw/_/TranslateWebserverUi/data/batchexecute?\
            rpcids=MkEWBc&\
            f.sid=4622116653376551039&\
            bl=boq_translate-webserver_20210414.13_p0&\
            hl=zh-TW&\
            soc-app=1&\
            soc-platform=1&\
            soc-device=1&\
            _reqid=1737851&\
            rt=c"

        self.HEADER = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }

        # can't sure whether it works for everyone, token in this URL might been blocked.
        self.DATA = "f.req=%5B%5B%5B%22MkEWBc%22%2C%22%5B%5B%5C%22{}%5C%22%2C%5C%22{}%5C%22%2C%5C%22{}%5C%22%2Ctrue%5D%2C%5Bnull%5D%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at=AD08yZn6jdbpV8qLjfergSwRT4IO%3A1618543754261&"

    def loadLanguageCode(self):
        with open(CONFIG_DIR + 'LanguageCode.csv') as fp:
            data = fp.readlines()
            data = [line.replace('\n', '') for line in data]

        for line in data:
            country, code = line.split(',')
            self.languageCode[country] = code
            if code==self.fr: self.inputLanguage = country
            if code==self.to: self.outputLanguage = country

    def translate(self, text):
        '''
            return a string which translate from self.fr to self.to
        '''
        # send request
        text = quote(text)
        response = requests.post(
            self.URL,
            data=self.DATA.format(text, self.fr, self.to),
            headers=self.HEADER
        )
        lines = response.text.split('\n')
        targetLine = ""
        for i in range(2, len(lines)):
            targetLine += lines[i]

        # replace useless char
        # change JSON format to Python format because we will use this string to generate Python code
        replaceDict = {
            '\\n': '',
            'null': 'None',
            'true': 'True',
            'false': 'False'
        }
        for item in replaceDict:
            targetLine = targetLine.replace(item, replaceDict[item])

        # get information block
        data = eval(targetLine)
        data = eval(data[0][2])

        ans = []
        for i in data[1][0][0][5]:
            ans.append(i[0])
        return ans

class TranslatorApp(npyscreen.NPSAppManaged):

    translator = GoogleTranslator(config['inputLanguage'], config['outputLanguage'])

    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        self.addForm("MAIN", MainForm, name="Google Translator - TUI")
        self.addForm("LANGUAGE", LanguageForm, name="LANGUAGE CHOOSE")

if __name__ == "__main__":
    app = TranslatorApp()
    app.run()
