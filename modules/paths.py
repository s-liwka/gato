import platform
import os
import tempfile

tmp = tempfile.gettempdir()

def get_config_file_dir():
    if platform.system() == 'Linux':
        if os.environ.get('ANDROID_ROOT') is None:
            config_dir = os.path.join(os.path.expanduser('~'), '.config', 'sliwkas-selfbot')  
        else:
            config_dir = os.path.join(os.getenv("EXTERNAL_STORAGE"), 'sliwkas-selfbot')
    elif platform.system() == 'Windows':
        config_dir = os.path.join(os.environ['LOCALAPPDATA'], 'sliwkas-selfbot')
    else:
        print(f'Unsupported platform {platform.system()}')
        exit()

    config_file = os.path.join(config_dir, 'config.json')
    return config_file, config_dir
