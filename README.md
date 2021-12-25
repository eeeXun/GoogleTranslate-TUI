# GoogleTranslate-TUI

Google Translate client on your console (Unofficial)

![](Screenshot_20211224_150251.png)

## Warning

It use Google Translate's API(free), so it may not work when you send too many requests.

**It just a practice for npyscreen, this respository may not update any more.**

## Usage
- Install packages
    - `pip install -r requirements.txt`

- Install program (⚠️Make sure your `~/.local/bin` is under the `$PATH`)
    - `make install`

- Change Language Settings: `vim ~/.config/pylate/config.json`
    - You can find Language Code in [ISO-639-1](https://en.wikipedia.org/wiki/ISO_639-1) or [Google Support](https://cloud.google.com/translate/docs/languages) or `LanguageCode.csv`
    ```
        {
            "inputLanguage": "en",
            "outputLanguage": "zh-TW"
        }
    ```

- Start
    - `pylate`

## Controls
- General
    - Send Request: `ALT + ENTER`
    - Swap Language: `CTRL + T`
    - Delete all input: `CTRL + D`
    - Exit: `Ctrl + Q`
    - Select Language: `Ctrl + S`
        - Select other Widget: `TAB`/`Shift+TAB`
        - Select: `ENTER`
- Sound
    - Play Sound on left: `CTRL + K`
    - Play Sound on right: `CTRL + L`
