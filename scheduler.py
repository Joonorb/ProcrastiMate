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

restricted_programs = set()
monitored_websites = set()
job_mapping = {}  # Global job mapping

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

    # Set global event to manage the blocking thread
    global block_thread_event
    block_thread_event.clear()  # Ensure event is not set
    monitoring_thread = Thread(target=block_restricted_programs, daemon=True)
    monitoring_thread.start()

    for program in open_programs:
        if program in restricted_programs:
            notify(f"Program {program} cannot be opened during task '{name}' duration.")
        else:
            try:
                subprocess.Popen(program)
                print(f"Opened program: {program}")
            except Exception as e:
                print(f"Error opening application: {program}. Exception: {e}")

    websites_to_block = [url.strip() for url in websites_to_block]
    print(f"Blocking websites: {websites_to_block}")
    block_websites(websites_to_block)
    monitored_websites.update(websites_to_block)

    # Restart Chrome to apply website blocking
    restart_chrome()

def end_task(name, restrict_programs, open_programs, websites_to_unblock):
    global restricted_programs, monitored_websites

    restricted_programs.difference_update(restrict_programs)

    websites_to_unblock = [url.strip() for url in websites_to_unblock]
    print(f"Unblocking websites: {websites_to_unblock}")
    unblock_websites(websites_to_unblock)
    monitored_websites.difference_update(websites_to_unblock)

    # Restart Chrome to apply website unblocking
    restart_chrome()

def notify_before_task(name, restrict_programs, websites_to_block):
    message = (f"Task '{name}' will begin in two minutes. "
               f"Programs to be restricted: {', '.join([os.path.basename(p) for p in restrict_programs])}. "
               f"Websites to be blocked: {', '.join(websites_to_block)}. "
               "Please save your work. Chrome will restart.")
    notification.notify(
        title="Upcoming Task Notification",
        message=message,
        timeout=10  # notification stays for 10 seconds
    )
    print(message)

def send_notification(name, restrict_programs, websites_to_block):
    notify_before_task(name, restrict_programs, websites_to_block)

def run_scheduler():
    print("Scheduler is running...")
    while True:
        schedule.run_pending()
        time.sleep(1)

tasks = []

def schedule_task(name, start_time, end_time, restrict_programs, open_programs, websites, notify_websites):
    today = datetime.today()
    start_time_dt = datetime.strptime(start_time, '%H:%M').replace(year=today.year, month=today.month, day=today.day)
    end_time_dt = datetime.strptime(end_time, '%H:%M').replace(year=today.year, month=today.month, day=today.day)

    notify_time_dt = start_time_dt - timedelta(minutes=2)

    # Schedule notification
    notify_job = schedule.every().day.at(notify_time_dt.strftime('%H:%M')).do(send_notification, name, restrict_programs, websites)

    # Schedule task start and end
    start_job = schedule.every().day.at(start_time_dt.strftime('%H:%M')).do(start_task, name, restrict_programs, open_programs, websites)
    end_job = schedule.every().day.at(end_time_dt.strftime('%H:%M')).do(end_task, name, restrict_programs, open_programs, websites)

    # Map jobs to task name
    job_mapping[name] = [notify_job, start_job, end_job]

    # Add task to the list
    task = {
        "name": name,
        "start_time": start_time,
        "end_time": end_time,
        "restrict_programs": restrict_programs,
        "open_programs": open_programs,
        "websites": websites
    }
    tasks.append(task)

def get_all_tasks():
    return tasks

def remove_task_by_name(task_name):
    global tasks, job_mapping

    # Remove task from list
    tasks = [task for task in tasks if task["name"] != task_name]

    # Cancel scheduled jobs
    if task_name in job_mapping:
        for job in job_mapping[task_name]:
            schedule.cancel_job(job)
        del job_mapping[task_name]

    # Stop the blocking thread if it was running
    global block_thread_event
    block_thread_event.set()  # Signal the thread to stop


if __name__ == "__main__":
    run_scheduler()
