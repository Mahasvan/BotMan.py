# BotMan.py Rewrite

-----------

## Work-in-progress rewrite of [BotMan.py](https://github.com/code-cecilia/botman.py) using py-cord instead of discord.py.

## Sections
- [Config Structure](#config-structure)
- [Dependencies](#dependencies)
- [Misc Dependencies](#misc-dependencies)
- [Dependencies Used By Each Cog](#dependencies-used-by-each-cog)
- [Adding Cogs to Blacklist](#adding-cogs-to-blacklist)


### Config Structure
```json
{
  "bot_token": "",
  "bot_owner_id": 123456789,
  "bot_prefix": "",
  "bot_description": "The coolest Python bot on the planet!",
  "bot_stream": true,
  "bot_stream_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",

  "blacklisted_cogs": ["cog1", "cog2"],

  "imgflip_username": "",
  "imgflip_password": "",

  "weather_api_key": "",

  "spotify_client_id": "",
  "spotify_client_secret": "",

  "topgg_token": "",

  "reddit_username": "",
  "reddit_password": "",
  "reddit_client_id": "",
  "reddit_client_secret": "",

  "currency_api_key": "",

  "openrobot_api_key": "",

  "tesseract_custom_path": "",
  "tesseract_tessdata_path": ""

}
```

### Dependencies
This project uses a list of dependencies which can be found in the [requirements file](requirements.txt). 
You can install them using the following command:
```shell
# macOS
python3 -m pip install -r requirements.txt

# Windows
python -m pip install -r requirements.txt

# Linux (Works on my Ubuntu machine, I don't really know about other distros)
python3 -m pip install -r requirements.txt
```

In case you are hosting the bot in an obscure environment, like a very old jailbroken iPad _(don't.)_, you might find that 
not all dependencies can be installed on your machine.
In that case, you can install the available dependencies manually, 
then add the cogs which use the unavailable dependencies to the `blacklisted_cogs` array in the config.
A list of all dependencies each Cog uses can be found [here](#dependencies-used-by-each-cog).<br>
You can install a dependency manually by running the following command:
```shell
# macOS
python3 -m pip install <dependency>

# Windows
python -m pip install <dependency>

# Linux (Works on my Ubuntu machine, I don't really know about other distros)
python3 -m pip install <dependency>
```

### Misc Dependencies
Apart from the dependencies mentioned in the `requirements.txt` file, there are a few non-python dependencies which need to be installed manually.

- `tesseract-ocr`
    - For Linux:
  ```shell
  # Works on my Ubuntu machine, I don't really know about other distros
  sudo apt-get install tesseract-ocr
  # Install all available languages
  sudo apt-get install tesseract-ocr-all
  ```
    - For macOS:
  ```shell
  # You need Homebrew for this
  brew install tesseract
  # Install all available languages
  brew install tesseract-lang
  ```    
  - For Windows
  ```
  # There is no official installer, but this one works just fine
  Download from https://github.com/UB-Mannheim/tesseract/wiki
  ```

- `neofetch` (not very important, but nice to have)
  - [Installation Instructions](https://github.com/dylanaraps/neofetch/wiki/Installation)


### Dependencies Used by each Cog
Common dependencies to every Cog:
- `py-cord`

Dependencies used by:

| Cog                 | Dependencies                                       |
|---------------------|----------------------------------------------------|
| bot_internal_events | aiohttp, requests                                  |
| botinfo             | aiohttp, speedtest-cli                             |
| covid               | aiohttp                                            |
| currency            | aiohttp                                            |
| funzies             | aiohttp                                            |
| gaems               | aiohttp                                            |
| image_processing    | aiohttp, pillow, pytesseract, numpy, opencv-python |
| info                | None                                               |
| links               | None                                               |
| logging             | None                                               |
| madlibs             | aiohttp                                            |
| memes               | aiohttp                                            |
| misc                | aiohttp                                            |
| openrobot           | aiohttp                                            |
| owner_only          | aiohttp, jishaku                                   |
| roleplay            | aiohttp                                            |
| server_setup        | None                                               |
| spotify             | aiohttp, spotipy                                   |
| time_commands       | aiohttp                                            |
| topgg_commands      | topggpy                                            |
| translate           | googletrans                                        |
| weather             | aiohttp                                            |
| websurf             | aiohttp                                            |
| wikipedia           | aiohttp                                            |

### Adding Cogs to Blacklist
If you want to add a cog to the blacklist, add it to the `blacklisted_cogs` array in the config.

For example, if you don't want the `owner_only.py` to be loaded, add `owner_only` to the `blacklisted_cogs` array.
A sample array would be something like
```json
["owner_only", "spotify", "covid"]
```



# Work in Progress.