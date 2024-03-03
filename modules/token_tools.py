import requests
import modules.paths
from cryptography.fernet import Fernet
import os

def validate(token):
    headers = {"Authorization": token}
    response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
    if response.status_code == 401:
        return 'invalid'
    elif response.status_code != 200:
        return 'err'
    elif response.status_code == 200:
        return 'valid'

def get_encryption_key():
    config_file, config_dir = modules.paths.get_config_file_dir()
    with open(os.path.join(config_dir, 'token_encryption_key'), 'rb') as f:
        key = f.read()

    return key

def decrypt_token(token):
    key = get_encryption_key()
    cipher_suite = Fernet(key)
    decrypted_token = str(cipher_suite.decrypt(token).decode('utf-8')).replace('"', '')

    return decrypted_token

def encrypt_token(token):
    key = get_encryption_key()
    cipher_suite = Fernet(key)

    return cipher_suite.encrypt(token)
    
