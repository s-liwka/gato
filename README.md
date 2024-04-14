#   Gato

An utility selfbot for Discord!

## Installation

This is now designed to run on Linux only, more specifically a VPS. Python (duh) and libvips are required

Ubuntu:
```
apt install libvips python3 git python3.11-venv
```

Arch:
```
pacman -S libvips python git
```

Clone the repo:
```
git clone https://github.com/s-liwka/gato.git
```

Make a venv and install the requirements
```
cd gato
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Configure the selfbot:
```
python3 config.py configurator
```

Run:
```
python3 bot.py
```


If you ever want to update just run `git pull` in the gato directory


## Disclaimer

Discord is trademark of Discord Inc. and solely mentioned for the sake of descriptivity. Mention of it does not imply any affiliation with or endorsement by Discord Inc.
[Using Gato violates Discord's terms of service.](https://support.discord.com/hc/en-us/articles/115002192352-Automated-user-accounts-self-bots)
