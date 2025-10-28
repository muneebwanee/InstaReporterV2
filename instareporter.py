#!/usr/bin/env python3
import os
import sys
import asyncio
from colorama import init, Fore, Style
from src.instagram_api import InstagramAPI
from src.proxy_manager import ProxyManager
from src.utils import (
    print_banner,
    print_status,
    print_success,
    print_error,
    load_config
)

init(autoreset=True)

async def main():
    print_banner()
    
    # Load configuration
    config = load_config()
    
    # Initialize managers
    proxy_manager = ProxyManager(config.get('proxy_file'))
    api = InstagramAPI(proxy_manager)
    
    while True:
        print("\n" + "="*50)
        print(f"{Fore.CYAN}1. Report Profile")
        print(f"2. Report Post")
        print(f"3. Configure Proxies")
        print(f"4. Exit{Style.RESET_ALL}")
        print("="*50)
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            username = input("Enter target profile username: ")
            reason = input("Enter report reason (spam/abuse/other): ")
            await report_profile(api, username, reason)
            
        elif choice == "2":
            post_url = input("Enter post URL: ")
            reason = input("Enter report reason (spam/abuse/other): ")
            await report_post(api, post_url, reason)
            
        elif choice == "3":
            await configure_proxies(proxy_manager)
            
        elif choice == "4":
            print_success("Exiting InstaReporter...")
            sys.exit(0)
            
        else:
            print_error("Invalid choice!")

async def report_profile(api: InstagramAPI, username: str, reason: str):
    try:
        success = await api.report_profile(username, reason)
        if success:
            print_success(f"Successfully reported profile: {username}")
        else:
            print_error(f"Failed to report profile: {username}")
    except Exception as e:
        print_error(f"Error reporting profile: {str(e)}")

async def report_post(api: InstagramAPI, post_url: str, reason: str):
    try:
        success = await api.report_post(post_url, reason)
        if success:
            print_success(f"Successfully reported post: {post_url}")
        else:
            print_error(f"Failed to report post: {post_url}")
    except Exception as e:
        print_error(f"Error reporting post: {str(e)}")

async def configure_proxies(proxy_manager: ProxyManager):
    try:
        print_status("Configuring proxies...")
        await proxy_manager.load_proxies()
        print_success("Proxies configured successfully!")
    except Exception as e:
        print_error(f"Error configuring proxies: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_success("\nExiting InstaReporter...")
        sys.exit(0)
