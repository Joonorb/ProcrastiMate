import os
import psutil
import subprocess
import time
import platform

restricted_programs = set()

def block_application(application_path):
    executable_name = os.path.basename(application_path)

    blocked = False
    for process in psutil.process_iter(['name', 'exe']):
        if process.info['name'].lower() == executable_name.lower():
            try:
                process.kill()
                print(f"Blocked application: {application_path}")
                blocked = True
            except psutil.NoSuchProcess:
                print(f"Process {executable_name} no longer exists.")
            except psutil.AccessDenied:
                print(f"Access denied when trying to block {executable_name}.")
            except Exception as e:
                print(f"Error blocking application: {application_path}. Exception: {e}")
    if not blocked:
        print(f"Application at {application_path} not found or could not be blocked.")

def unblock_application(application_path):
    try:
        subprocess.Popen(application_path)
        print(f"Unblocked (opened) application: {application_path}")
    except FileNotFoundError:
        print(f"File not found: {application_path}.")
    except Exception as e:
        print(f"Error opening application: {application_path}. Exception: {e}")

def block_websites(websites):
    hosts_file_path = r"C:\Windows\System32\drivers\etc\hosts"
    try:
        with open(hosts_file_path, "r+") as file:
            lines = file.readlines()
            file.seek(0, os.SEEK_END)
            blocked_domains = set()
            for website in websites:
                domain = website.replace('https://', '').replace('http://', '').split('/')[0].strip()
                # Add www and non-www versions
                blocked_domains.add(domain)
                blocked_domains.add(f"www.{domain}")
            for domain in blocked_domains:
                if all(f"127.0.0.1 {domain}" not in line for line in lines):
                    file.write(f"127.0.0.1 {domain}\n")
        print(f"Blocked websites: {websites}")
    except Exception as e:
        print(f"Error blocking websites: {e}")

def unblock_websites(websites):
    hosts_file_path = r"C:\Windows\System32\drivers\etc\hosts"
    try:
        with open(hosts_file_path, "r") as file:
            lines = file.readlines()
        with open(hosts_file_path, "w") as file:
            blocked_domains = set()
            for website in websites:
                domain = website.replace('https://', '').replace('http://', '').split('/')[0].strip()
                # Add www and non-www versions
                blocked_domains.add(domain)
                blocked_domains.add(f"www.{domain}")
            for line in lines:
                if not any(domain in line for domain in blocked_domains):
                    file.write(line)
        print(f"Unblocked websites: {websites}")
    except Exception as e:
        print(f"Error unblocking websites: {e}")

def restart_chrome():
    if platform.system() == 'Windows':
        os.system('taskkill /im chrome.exe /f')
    elif platform.system() == 'Darwin':
        os.system('pkill -x "Google Chrome"')
    elif platform.system() == 'Linux':
        os.system('pkill -f "chrome"')

    # Wait for a moment to ensure Chrome has been completely closed
    time.sleep(2)

    # Start Chrome again
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            subprocess.Popen(path)
            break
    else:
        print("Chrome executable not found. Please verify the installation path.")
