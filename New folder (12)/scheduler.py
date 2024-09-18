import schedule
import time
import subprocess
import os
import psutil
from threading import Thread, Event
from blocker import block_application, unblock_application, block_websites, unblock_websites, restart_chrome
from notifications import notify
from plyer import notification
from datetime import datetime, timedelta
import json

restricted_programs = set()
monitored_websites = set()

# Global to manage blocking thread
block_thread_event = Event()

def block_restricted_programs():
    while not block_thread_event.is_set():
        for program in restricted_programs:
            for process in psutil.process_iter(['name']):
                if process.info['name'].lower() == os.path.basename(program).lower():
                    try:
                        process.kill()
                        notify(f"Program {program} was forcibly closed because it is restricted.")
                    except psutil.NoSuchProcess:
                        pass
                    except psutil.AccessDenied:
                        notify(f"Access denied when trying to block {program}.")
                    except Exception as e:
                        notify(f"Error blocking application {program}. Exception: {e}")
        time.sleep(5)  # Check every 5 seconds

def start_task(name, restrict_programs, open_programs, websites_to_block):
    global restricted_programs, monitored_websites

    for program in restrict_programs:
        block_application(program)
    restricted_programs.update(restrict_programs)

    for website in websites_to_block:
        block_websites(website)
    monitored_websites.update(websites_to_block)

    for program in open_programs:
        if not any(p.lower() == os.path.basename(program).lower() for p in psutil.process_iter(['name'])):
            try:
                subprocess.Popen(program)
            except Exception as e:
                notify(f"Error opening application {program}. Exception: {e}")

    notify(f"Task '{name}' started. Restrictions are now in place.")

    # Ensure blocking runs in a separate thread
    global block_thread_event
    block_thread_event.clear()
    blocking_thread = Thread(target=block_restricted_programs)
    blocking_thread.daemon = True
    blocking_thread.start()

def end_task(name):
    global restricted_programs, monitored_websites

    for program in restricted_programs:
        unblock_application(program)
    restricted_programs.difference_update(restricted_programs)

    for website in monitored_websites:
        unblock_websites(website)
    monitored_websites.difference_update(monitored_websites)

    notify(f"Task '{name}' ended. Restrictions have been lifted.")

    # Stop the blocking thread
    block_thread_event.set()

def schedule_task(name, start_time, end_time, restrict_programs, open_programs, websites_to_block, websites):
    start_dt = datetime.strptime(start_time, '%H:%M')
    end_dt = datetime.strptime(end_time, '%H:%M')

    now = datetime.now()
    start_time_today = now.replace(hour=start_dt.hour, minute=start_dt.minute, second=0, microsecond=0)
    end_time_today = now.replace(hour=end_dt.hour, minute=end_dt.minute, second=0, microsecond=0)

    if end_time_today < start_time_today:
        end_time_today += timedelta(days=1)

    schedule.every().day.at(start_time_today.strftime('%H:%M')).do(start_task, name, restrict_programs, open_programs, websites_to_block)
    schedule.every().day.at(end_time_today.strftime('%H:%M')).do(end_task, name)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def get_all_tasks():
    tasks = []
    for job in schedule.get_jobs():
        if job.job_func.__name__ == 'start_task':
            task_info = {
                'name': job.args[0],
                'start_time': job.at,
                'end_time': None,  # To be filled with a later job
                'restrict_programs': job.args[1],
                'open_programs': job.args[2],
                'websites': job.args[3]
            }
            # Find the corresponding end_task job
            for end_job in schedule.get_jobs():
                if end_job.job_func.__name__ == 'end_task' and end_job.args[0] == job.args[0]:
                    task_info['end_time'] = end_job.at
                    break
            tasks.append(task_info)
    return tasks

def remove_task_by_name(task_name):
    for job in schedule.get_jobs():
        if job.job_func.__name__ in ['start_task', 'end_task'] and job.args[0] == task_name:
            schedule.cancel_job(job)
