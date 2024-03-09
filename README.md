#   Gato

An utility selfbot for Discord!

## Installation

### Binaries
[Prerequisites: libvips](https://github.com/s-liwka/gato/wiki/Installing-libvips-on-Windows)

Binaries are avaliable only for Windows because getting gato to work using the latest commit is very easy on Linux. Just look at the **Latest commit** section below.

Binaries can be found in the [releases](https://github.com/s-liwka/gato/releases) page.

#### Why is my antivirus detecting it as malware??

Because i used a tool called pyinstaller to package it. A lot of skids also use it to package their shitty grabbers and rats, and now antiviruses will just take anything packaged by pyinstaller as malware. (especially if the code mentions discord, as a lot of those also use discord as a "control panel")


### Latest commit
Prerequisites: python 3.11, git, libvips


#### Linux

Prerequisites can be installed using your package manager. eg.
```sh
pacman -S libvips python git
```

Download setup.sh from scripts and run it as root. (with sudo, doas etc)

#### Windows

[libvips](https://github.com/s-liwka/gato/wiki/Installing-libvips-on-Windows)

[git](https://git-scm.com/download/win) - **when installing, select the add git to path option!**

[python](https://www.python.org/downloads/) - **also select add to path!**

Download setup.bat from scripts and run it.

## Usage

### Linux

A desktop file should've been created, and you should be able to find Gato using your launcher.
You can also run it from the terminal using `gato-gui`. If you wish to use the CLI version then run `gato-cli --help`

If you cant find it in your launcher, try copying over the .desktop file from resources, and pasting it into `/usr/share/applications`

### Windows

If you downloaded the binary, then double click it. **DO NOT MOVE THE BINARY AWAY FROM THE FOLDER.**

If you used the setup.bat script, then a shortcut on your desktop should've been created. The files have been installed at `C:\Program Files\gato`. You can run the CLI by cd'ing into that directory and running `python cli.py`


## Updating

### Linux

Run `gato-update` as root.

### Windows

If you downloaded the binary then you need to redownload it every new release.

If you used setup.bat then go to `C:\Program Files\gato\scripts` and run the `gato-update.bat` script.

## Disclaimer

Discord is trademark of Discord Inc. and solely mentioned for the sake of descriptivity. Mention of it does not imply any affiliation with or endorsement by Discord Inc.
[Using Gato violates Discord's terms of service.](https://support.discord.com/hc/en-us/articles/115002192352-Automated-user-accounts-self-bots)
