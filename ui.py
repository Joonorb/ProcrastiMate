import tkinter as tk
import customtkinter as ctk
from programs import get_installed_programs
from blocker import block_application, unblock_application
from scheduler import schedule_task, run_scheduler, get_all_tasks, remove_task_by_name
import threading

def create_ui():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("ProcrastiMate")

    dark_bg_color = "#2e2e2e"  # Dark background color for listbox
    dark_fg_color = "#ffffff"  # White text color for listbox

    font_family = "Helvetica"
    font_size = 14
    font = (font_family, font_size)

    padding_x = 20
    padding_y = 20
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    frame = ctk.CTkFrame(root)
    frame.grid(sticky="nsew", padx=padding_x, pady=padding_y)

    frame.grid_columnconfigure(1, weight=1)

    # ... (rest of your UI setup code remains unchanged)


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

        schedule_task(name, start_time, end_time, restrict_programs, open_programs, websites, websites)
        update_existing_tasks()

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
                remove_task_by_name(task['name'])
                update_existing_tasks()

    ctk.CTkLabel(frame, text="Task Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    name_entry = ctk.CTkEntry(frame, font=font)
    name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(frame, text="Start Time:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    start_time_entry = ctk.CTkEntry(frame, font=font)
    start_time_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(frame, text="End Time:").grid(row=2, column=0, padx=10, pady=(5,50), sticky="w")
    end_time_entry = ctk.CTkEntry(frame, font=font)
    end_time_entry.grid(row=2, column=1, padx=10, pady=(5,50), sticky="ew")

    ctk.CTkLabel(frame, text="Select Programs to Restrict:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    restrict_program_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=60, height=10, bg=dark_bg_color, fg=dark_fg_color)
    restrict_program_listbox.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(frame, text="Search Restrict Programs:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    restrict_search_entry = ctk.CTkEntry(frame, font=font)
    restrict_search_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(frame, text="Selected Programs to Restrict:").grid(row=5, column=0, padx=10, pady=(5,50), sticky="w")
    restrict_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=60, height=5, bg=dark_bg_color, fg=dark_fg_color)
    restrict_listbox.grid(row=5, column=1, padx=10, pady=(5,50), sticky="ew")
    restrict_listbox.bind('<ButtonRelease-1>', lambda e: remove_program(e, restrict_listbox))

    ctk.CTkLabel(frame, text="Select Programs to Open:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
    open_program_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=60, height=10, bg=dark_bg_color, fg=dark_fg_color)
    open_program_listbox.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(frame, text="Search Open Programs:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
    open_search_entry = ctk.CTkEntry(frame, font=font)
    open_search_entry.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(frame, text="Selected Programs to Open:").grid(row=8, column=0, padx=10, pady=(5,50), sticky="w")
    open_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=60, height=5, bg=dark_bg_color, fg=dark_fg_color)
    open_listbox.grid(row=8, column=1, padx=10, pady=(5,50), sticky="ew")
    open_listbox.bind('<ButtonRelease-1>', lambda e: remove_program(e, open_listbox))

    ctk.CTkLabel(frame, text="Block Websites (comma-separated):").grid(row=9, column=0, padx=10, pady=5, sticky="w")
    websites_entry = ctk.CTkEntry(frame, font=font)
    websites_entry.grid(row=9, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkButton(frame, text="Add Task", command=add_task).grid(row=10, column=0, columnspan=2, padx=10, pady=5)

    ctk.CTkLabel(frame, text="Existing Tasks:").grid(row=11, column=0, columnspan=2, padx=10, pady=5)
    existing_tasks_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=120, height=10, bg=dark_bg_color, fg=dark_fg_color)
    existing_tasks_listbox.grid(row=12, column=0, columnspan=2, padx=10, pady=5)

    ctk.CTkButton(frame, text="Remove Task", command=remove_task).grid(row=13, column=0, columnspan=2, padx=10, pady=5)

    programs = get_installed_programs()
    for program in programs:
        restrict_program_listbox.insert(tk.END, f"{program[0]} {{{program[1]}}}")
        open_program_listbox.insert(tk.END, f"{program[0]} {{{program[1]}}}")

    restrict_search_entry.bind('<KeyRelease>', restrict_search)
    open_search_entry.bind('<KeyRelease>', open_search)

    restrict_program_listbox.bind('<<ListboxSelect>>', lambda e: select_program(e, restrict_program_listbox, restrict_listbox))
    open_program_listbox.bind('<<ListboxSelect>>', lambda e: select_program(e, open_program_listbox, open_listbox))

    threading.Thread(target=run_scheduler, daemon=True).start()

    update_existing_tasks()

    root.mainloop()

if __name__ == "__main__":
    create_ui()
