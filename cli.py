import argparse
from multiprocessing import Process, Queue

import modules.token_tools
import modules.paths
import bot
import json
import time
import os

class BooleanAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values.lower() in ('yes', 'true', 't', 'y', '1'):
            setattr(namespace, self.dest, True)
        elif values.lower() in ('no', 'false', 'f', 'n', '0'):
            setattr(namespace, self.dest, False)
        else:
            raise argparse.ArgumentError(self, f"Invalid boolean value: {values}")

def yes_no(message):
    while True:
        response = input(message)
        if response.lower() == 'y':
            return True
        elif response.lower() == 'n':
            return False
        else:
            print('Invalid selection.')



def load_config():
    config_file, config_dir = modules.paths.get_config_file_dir()
    with open(config_file, 'r') as f:
        config = json.load(f)

        return config

if __name__ == "__main__":

    config_file, config_dir = modules.paths.get_config_file_dir()

    parser = argparse.ArgumentParser(description='Gato CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    ###########################################################################################################################

    run_parser = subparsers.add_parser('run', help='Run gato')
    run_parser.add_argument('--unencrypted_token', action='store_true', help="Won't attempt to decrypt the token while starting")

    ###########################################################################################################################
    config_parser = subparsers.add_parser('config', help='Configure gato')
    config_subparsers = config_parser.add_subparsers(dest='config_option', help='Configuration option to set')

    sniper_parser = config_subparsers.add_parser('sniper', help='Enable or disable the nitro sniper')
    sniper_parser.add_argument('value', action=BooleanAction, help='True to enable, False to disable')

    token_parser = config_subparsers.add_parser('token', help='Set the token')
    token_parser.add_argument('value', type=str, help='The token value')
    token_parser.add_argument('--dont_encrypt', action='store_true', help="Won't encrypt the token while configuring")

    delete_after_time_parser = config_subparsers.add_parser('delete_after_time', help='Set the delete after time')
    delete_after_time_parser.add_argument('value', type=float, help='The time in seconds before the self-bot deletes its own messages')

    prompt_for_destructive_parser = config_subparsers.add_parser('prompt_for_destructive', help='Enable or disable prompt for destructive actions')
    prompt_for_destructive_parser.add_argument('value', action=BooleanAction, help='True to enable, False to disable')

    logger_parser = config_subparsers.add_parser('logger', help='Enable or disable the message logger')
    logger_parser.add_argument('value', action=BooleanAction, help='True to enable, False to disable')

    prefix_parser = config_subparsers.add_parser('prefix', help="Set gato's prefix")
    prefix_parser.add_argument('value', type=str, help="The prefix")

    ###########################################################################################################################

    configurator_parser = subparsers.add_parser('configurator', help='Set-up gato')
    configurator_parser.add_argument('--dont_encrypt', action='store_true', help="Won't encrypt the token while configuring")

    args = parser.parse_args()

    if args.command == 'run':
        config = load_config()
        print("[INFO] Starting gato...\n")
        print("[INFO] Validating token...\n")

        if args.unencrypted_token:
            token = config['token']
        else:
            token = modules.token_tools.decrypt_token(config['token'])

        check_token = modules.token_tools.validate(token)

        if check_token == 'invalid':
            print("[ERR] Invalid token.")
            exit()
        elif check_token == 'err':
            print("[WARN] An error has occured while validating the token. Continuing...\n")
        else:
            print("[SUCCESS] Valid token.")

        queue = Queue()
        bot_process = Process(target=bot.main, args=(token, queue))
        bot_process.daemon = True
        bot_process.start()

        
        while True:
            if not queue.empty():
                print(queue.get())
            time.sleep(0.1)
    

    if args.command == 'config':
        config = load_config()

        if args.config_option == 'sniper':
            config['sniper'] = args.value
        elif args.config_option == 'delete_after_time':
            config['delete_after_time'] = args.value
        elif args.config_option == 'prompt_for_destructive':
            config['prompt_for_destructive'] = args.value
        elif args.config_option == 'logger':
            config['logger'] = args.value
        elif args.config_option == 'prefix':
            config['prefix'] = args.value
        elif args.config_option == 'token':

            token = args.value.replace('"', '')
            validate = modules.token_tools.validate(token)
            if validate != 'valid':
                if validate == 'invalid':
                    print("WARNING: INVALID TOKEN")
                elif validate == 'err':
                    print("WARNING: AN ERROR HAS OCCURED WHILE CHECKING THE TOKEN")

            if args.dont_encrypt:
                config['token'] =  token
            else:
                config['token'] = modules.token_tools.encrypt_token(token.encode('utf-8')).decode('utf-8')

        with open(config_file, 'w') as f:
            json.dump(config, f)
        print(f"Update the value {args.config_option} to {args.value}")
                


    if args.command == 'configurator':
        config_file, config_dir = modules.paths.get_config_file_dir()
        while True:
            token = input("Your token: ")
            token = token.replace('"', '')
            validate = modules.token_tools.validate(token)
            if validate != 'valid':
                if validate == 'invalid':
                    continue_anyway = input('This token is invalid. Continue anyways? (y/n) ')
                    if continue_anyway.lower() == 'y': break
                    else: pass
                elif validate == 'err':
                    continue_anyway = input('An error has occured while checking the token. Continue anyways? (y/n) ')
                    if continue_anyway.lower() == 'y': break
                    else: pass
            else:
                break
        
        prefix = input("Selfbot prefix: ")
        
        sniper = yes_no("Enable the nitro sniper? (y/n) ")
        logger = yes_no("Do you want to enable the message logger? (y/n) ")
        profanity = yes_no("Do you want to keep track of your profanity? (y/n) ")
        prompt_for_destructive = yes_no("Do you want a prompt whenever you try to run some destructive action? (y/n) ")

        while True:
            delete_after_time = input("How much time do you want it to take before the self-bot deletes it's own messages? (Leave empty if you don't want that to happen) ")
            
            if not delete_after_time:
                delete_after_time = None
                break
            else:
                try:
                    delete_after_time = float(delete_after_time)
                    break
                except ValueError:
                    print("That's not a number")


        if not args.dont_encrypt:
            token = modules.token_tools.encrypt_token(token.encode('utf-8')).decode('utf-8')

        config = {
            "token": token,
            "prefix": prefix,
            "sniper": sniper,
            "profanity": profanity,
            "delete_after_time": delete_after_time,
            "prompt_for_destructive": prompt_for_destructive,
            "logger": logger
            }

        with open(config_file, 'w') as f:
            json.dump(config, f)

        print(f"Config saved to {config_file}\n")
