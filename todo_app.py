import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My To-Do List")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        
        # Data file for persistence
        self.data_file = "todo_data.json"
        self.tasks = []
        
        # Load existing tasks
        self.load_tasks()
        
        # Create GUI elements
        self.create_widgets()
        
        # Load tasks into the listbox
        self.refresh_task_list()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="📋 My To-Do List", 
                              font=("Arial", 18, "bold"), 
                              bg="#f0f0f0", fg="#333")
        title_label.pack(pady=10)
        
        # Input frame
        input_frame = tk.Frame(self.root, bg="#f0f0f0")
        input_frame.pack(pady=10, padx=20, fill="x")
        
        # Task entry
        self.task_entry = tk.Entry(input_frame, font=("Arial", 12), width=40)
        self.task_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        
        # Add button
        add_btn = tk.Button(input_frame, text="Add Task", 
                           command=self.add_task,
                           bg="#4CAF50", fg="white", 
                           font=("Arial", 10, "bold"),
                           padx=20)
        add_btn.pack(side="right")
        
        # Task list frame
        list_frame = tk.Frame(self.root, bg="#f0f0f0")
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Scrollbar and listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.task_listbox = tk.Listbox(list_frame, 
                                      yscrollcommand=scrollbar.set,
                                      font=("Arial", 11),
                                      selectmode=tk.SINGLE,
                                      height=15)
        self.task_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.task_listbox.yview)
        
        # Bind click event for checkbox clicking
        self.task_listbox.bind("<Button-1>", self.on_listbox_click)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10, padx=20)
        
        # Complete button
        complete_btn = tk.Button(button_frame, text="✓ Mark Complete", 
                                command=self.mark_complete,
                                bg="#2196F3", fg="white", 
                                font=("Arial", 10),
                                padx=15)
        complete_btn.pack(side="left", padx=5)
        
        # Edit button
        edit_btn = tk.Button(button_frame, text="✏️ Edit", 
                            command=self.edit_task,
                            bg="#FF9800", fg="white", 
                            font=("Arial", 10),
                            padx=15)
        edit_btn.pack(side="left", padx=5)
        
        # Delete button
        delete_btn = tk.Button(button_frame, text="🗑️ Delete", 
                              command=self.delete_task,
                              bg="#f44336", fg="white", 
                              font=("Arial", 10),
                              padx=15)
        delete_btn.pack(side="left", padx=5)
        
        # Clear completed button
        clear_btn = tk.Button(button_frame, text="Clear Completed", 
                             command=self.clear_completed,
                             bg="#673AB7", fg="white", 
                             font=("Arial", 10),
                             padx=15)
        clear_btn.pack(side="left", padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor="w", 
                             bg="#e0e0e0", font=("Arial", 9))
        status_bar.pack(side="bottom", fill="x")
        
        self.update_status()
        
    def add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            task = {
                "text": task_text,
                "completed": False,
                "created": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            self.tasks.append(task)
            self.task_entry.delete(0, tk.END)
            self.refresh_task_list()
            self.save_tasks()
            self.update_status()
        else:
            messagebox.showwarning("Warning", "Please enter a task!")
    
    def mark_complete(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            self.tasks[index]["completed"] = not self.tasks[index]["completed"]
            self.refresh_task_list()
            self.save_tasks()
            self.update_status()
        else:
            messagebox.showwarning("Warning", "Please select a task!")
    
    def edit_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            current_text = self.tasks[index]["text"]
            new_text = simpledialog.askstring("Edit Task", "Edit task:", initialvalue=current_text)
            if new_text and new_text.strip():
                self.tasks[index]["text"] = new_text.strip()
                self.refresh_task_list()
                self.save_tasks()
        else:
            messagebox.showwarning("Warning", "Please select a task to edit!")
    
    def delete_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            task_text = self.tasks[index]["text"]
            if messagebox.askyesno("Confirm Delete", f"Delete task: '{task_text}'?"):
                del self.tasks[index]
                self.refresh_task_list()
                self.save_tasks()
                self.update_status()
        else:
            messagebox.showwarning("Warning", "Please select a task to delete!")
    
    def clear_completed(self):
        completed_count = sum(1 for task in self.tasks if task["completed"])
        if completed_count > 0:
            if messagebox.askyesno("Confirm Clear", f"Clear {completed_count} completed task(s)?"):
                self.tasks = [task for task in self.tasks if not task["completed"]]
                self.refresh_task_list()
                self.save_tasks()
                self.update_status()
        else:
            messagebox.showinfo("Info", "No completed tasks to clear!")
    
    def on_listbox_click(self, event):
        """Handle clicks on the listbox, especially for checkbox area"""
        # Get the index of the clicked item
        index = self.task_listbox.nearest(event.y)
        if 0 <= index < len(self.tasks):
            # Check if click was in the checkbox area (roughly first 25 pixels)
            if event.x <= 25:
                # Toggle completion status
                self.tasks[index]["completed"] = not self.tasks[index]["completed"]
                self.refresh_task_list()
                self.save_tasks()
                self.update_status()
                return "break"  # Prevent normal selection behavior
    
    def refresh_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for i, task in enumerate(self.tasks):
            # Use larger checkbox characters
            status = "☑" if task["completed"] else "☐"
            display_text = f"{status} {task['text']}"
            self.task_listbox.insert(tk.END, display_text)
            
            # Color coding for completed tasks
            if task["completed"]:
                self.task_listbox.itemconfig(i, {"fg": "gray", "selectbackground": "#d0d0d0"})
            else:
                self.task_listbox.itemconfig(i, {"fg": "black", "selectbackground": "#0078d4"})
    
    def update_status(self):
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks if task["completed"])
        pending_tasks = total_tasks - completed_tasks
        
        status_text = f"Total: {total_tasks} | Pending: {pending_tasks} | Completed: {completed_tasks}"
        self.status_var.set(status_text)
    
    def save_tasks(self):
        try:
            with open(self.data_file, 'w') as file:
                json.dump(self.tasks, file, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tasks: {str(e)}")
    
    def load_tasks(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as file:
                    self.tasks = json.load(file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {str(e)}")
            self.tasks = []

def main():
    root = tk.Tk()
    app = TodoApp(root)
    
    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Handle window closing
    def on_closing():
        app.save_tasks()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()