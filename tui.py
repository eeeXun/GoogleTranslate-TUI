import npyscreen
import curses
from GoogleTranslator import GoogleTranslator

class TranslatorApp(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        self.addForm("MAIN", MainForm, name="Google Translator - TUI")

class Box(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLineEdit

class MainForm(npyscreen.FormBaseNew):
    def create(self):
        # set translator
        self.translator = GoogleTranslator('en', "zh_TW")

        # set event handler
        event_handlers = {
            # send request
            curses.ascii.alt(curses.ascii.NL): self.send_text,
            
            #exit
            "^Q": self.exit_app,

            # delete all input
            "^D": self.remove_text,
        }
        self.add_handlers(event_handlers)

        # get terminal's size
        y, x = self.useable_space()

        self.input = self.add(Box, name="Input (from)", footer=self.translator.fr, 
            max_width=x//2-5, max_height=y//3,
            relx=3, rely=3,
            value="Hello world"
        )
        
        self.output = self.add(Box, name="Output (to)", footer=self.translator.to,
            max_width=x//2-5, max_height=y//3,
            relx=x//2+2, rely=3,
            value="你好，世界", editable=False
        )

        self.readme = self.add(Box, name="README",
            max_width=x-5, max_height=y//3*2-6,
            relx=3, rely=y//3+4,
            value='''
        █▀▀ █▀█ █▀█ █▀▀ █░░ █▀▀ ▄▄ ▀█▀ █▀█ ▄▀█ █▄░█ █▀ █░░ ▄▀█ ▀█▀ █▀▀   ▀█▀ █░█ █
        █▄█ █▄█ █▄█ █▄█ █▄▄ ██▄ ░░ ░█░ █▀▄ █▀█ █░▀█ ▄█ █▄▄ █▀█ ░█░ ██▄   ░█░ █▄█ █
        
        This is an unofficial Google Translate client.
        It use Google Translate's API(free), so it may not work when you send too many requests.

        It just a practice for npyscreen, this respository may not update any more.

        -    ^Q           :         quit
        -    ALT + ENTER  :         search
        -    CTRL + D     :         delete all input
            ''',
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
    
    def send_text(self, event):
        '''
            use self.translator to send the request to Google Translate
            then update the response to self.output
        '''
        # When press ALT + ENTER, send request & update output's text
        if self.input.value != "":
            try:
                targetText = self.translator.translate(self.input.value)
            except:
                targetText = "This is not a true translation, there exist an error."
            finally:
                self.output.value = targetText

                # refresh entire form
                # Though npyscreen's documentation mention that we should avoid using DISPLAY() function
                # I can't display Chinese or Japanese,etc correctly when I didn't use this function.
                self.DISPLAY()
    
    def remove_text(self, event):
        self.input.value = ""
        self.input.update()

    def exit_app(self, event):
        exit(0)