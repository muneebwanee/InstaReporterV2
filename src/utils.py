import yaml
from typing import Dict
import os
from colorama import Fore, Style
from pyfiglet import figlet_format
from termcolor import colored

def print_banner():
    """Print tool banner"""
    banner = figlet_format("InstaReporter", font="slant")
    print(colored(banner, "cyan"))
    print(colored("By @muneebwanee", "yellow"))
    print("="*50)

def print_status(message: str):
    """Print status message"""
    print(f"{Fore.BLUE}[*]{Style.RESET_ALL} {message}")

def print_success(message: str):
    """Print success message"""
    print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {message}")

def print_error(message: str):
    """Print error message"""
    print(f"{Fore.RED}[-]{Style.RESET_ALL} {message}")

def load_config() -> Dict:
    """Load configuration from config.yml"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yml")
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}
