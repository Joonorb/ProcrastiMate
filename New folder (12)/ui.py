import tkinter as tk
from tkinter import ttk
from programs import get_installed_programs
from blocker import block_application, unblock_application
from scheduler import schedule_task, run_scheduler, get_all_tasks, remove_task_by_name
import threading
import json
import os

TASKS_FILE = 'tasks.json'

def save_tasks():
    with open(TASKS_FILE, 'w') as file:
        json.dump(get_all_tasks(), file)

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as file:
            tasks = json.load(file)
            for task in tasks:
                # Call schedule_task to re-schedule tasks
                schedule_task(task['name'], task['start_time'], task['end_time'],
                               task['restrict_programs'], task['open_programs'], task['websites'], task['websites'])

def create_ui():
    root = tk.Tk()
    root.title("Task Manager")

    def update_program_list(search_text, listbox, full_programs_list):
        listbox.delete(0, tk.END)
        filtered_programs = [p for p in full_programs_list if search_text.lower() in p[0].lower()]
        for program in filtered_programs:
            listbox.insert(tk.END, f"{program[0]} {{{program[1]}}}")

    def add_task():
        name = name_entry.get()
        start_time = start_time_entry.get()
        end_time = end_time_entry.get()
        restrict_programs = [program.split(' {')[1].rstrip('}') for program in restrict_listbox.get(0, tk.END)]
        open_programs = [program.split(' {')[1].rstrip('}') for program in open_listbox.get(0, tk.END)]
        websites = websites_entry.get().split(',')

        # Call schedule_task to handle the actual scheduling
        schedule_task(name, start_time, end_time, restrict_programs, open_programs, websites, websites)
        update_existing_tasks()
        save_tasks()  # Save tasks after adding

    def select_program(event, source_listbox, target_listbox):
        selected = source_listbox.curselection()
        if selected:
            program = source_listbox.get(selected[0])
            if program not in target_listbox.get(0, tk.END):
                target_listbox.insert(tk.END, program)

    def remove_program(event, listbox):
        selected = listbox.curselection()
        if selected:
            listbox.delete(selected[0])

    def restrict_search(event):
        search_text = restrict_search_entry.get()
        update_program_list(search_text, restrict_program_listbox, programs)

    def open_search(event):
        search_text = open_search_entry.get()
        update_program_list(search_text, open_program_listbox, programs)

    def update_existing_tasks():
        existing_tasks_listbox.delete(0, tk.END)
        tasks = get_all_tasks()
        for task in tasks:
            task_info = (f"Name: {task['name']}, Start: {task['start_time']}, End: {task['end_time']}, "
                         f"Restrict: {', '.join(task['restrict_programs'])}, Open: {', '.join(task['open_programs'])}, "
                         f"Websites: {', '.join(task['websites'])}")
            existing_tasks_listbox.insert(tk.END, task_info)

    def remove_task():
        selected_task_index = existing_tasks_listbox.curselection()
        if selected_task_index:
            task_index = selected_task_index[0]
            tasks = get_all_tasks()
            if 0 <= task_index < len(tasks):
                task = tasks[task_index]
                remove_task_by_name(task['name'])  # Remove task from scheduler
                update_existing_tasks()  # Refresh UI
                save_tasks()  # Save tasks after removing

    tk.Label(root, text="Task Name:").grid(row=0, column=0)
    name_entry = tk.Entry(root)
    name_entry.grid(row=0, column=1)

    tk.Label(root, text="Start Time:").grid(row=1, column=0)
    start_time_entry = tk.Entry(root)
    start_time_entry.grid(row=1, column=1)

    tk.Label(root, text="End Time:").grid(row=2, column=0)
    end_time_entry = tk.Entry(root)
    end_time_entry.grid(row=2, column=1)

    tk.Label(root, text="Select Programs to Restrict:").grid(row=3, column=0)
    restrict_program_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=10)
    restrict_program_listbox.grid(row=3, column=1)

    tk.Label(root, text="Search Restrict Programs:").grid(row=4, column=0)
    restrict_search_entry = tk.Entry(root)
    restrict_search_entry.grid(row=4, column=1)
    
    tk.Label(root, text="Selected Programs to Restrict:").grid(row=5, column=0)
    restrict_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=5)
    restrict_listbox.grid(row=5, column=1)
    restrict_listbox.bind('<ButtonRelease-1>', lambda e: remove_program(e, restrict_listbox))

    tk.Label(root, text="Select Programs to Open:").grid(row=6, column=0)
    open_program_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=10)
    open_program_listbox.grid(row=6, column=1)

    tk.Label(root, text="Search Open Programs:").grid(row=7, column=0)
    open_search_entry = tk.Entry(root)
    open_search_entry.grid(row=7, column=1)

    tk.Label(root, text="Selected Programs to Open:").grid(row=8, column=0)
    open_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=5)
    open_listbox.grid(row=8, column=1)
    open_listbox.bind('<ButtonRelease-1>', lambda e: remove_program(e, open_listbox))

    tk.Label(root, text="Block Websites (comma-separated):").grid(row=9, column=0)
    websites_entry = tk.Entry(root)
    websites_entry.grid(row=9, column=1)

    tk.Button(root, text="Add Task", command=add_task).grid(row=10, column=0, columnspan=2)

    # Section to display and manage existing tasks
    tk.Label(root, text="Existing Tasks:").grid(row=11, column=0, columnspan=2)
    existing_tasks_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=100, height=10)
    existing_tasks_listbox.grid(row=12, column=0, columnspan=2)

    tk.Button(root, text="Remove Task", command=remove_task).grid(row=13, column=0, columnspan=2)

    # Populate program listboxes
    programs = get_installed_programs()
    for program in programs:
        restrict_program_listbox.insert(tk.END, f"{program[0]} {{{program[1]}}}")
        open_program_listbox.insert(tk.END, f"{program[0]} {{{program[1]}}}")

    restrict_search_entry.bind('<KeyRelease>', restrict_search)
    open_search_entry.bind('<KeyRelease>', open_search)

    restrict_program_listbox.bind('<<ListboxSelect>>', lambda e: select_program(e, restrict_program_listbox, restrict_listbox))
    open_program_listbox.bind('<<ListboxSelect>>', lambda e: select_program(e, open_program_listbox, open_listbox))

    # Run scheduler in a separate thread
    threading.Thread(target=run_scheduler, daemon=True).start()

    load_tasks()  # Load tasks when initializing UI
    update_existing_tasks()

    root.mainloop()

if __name__ == "__main__":
    create_ui()
