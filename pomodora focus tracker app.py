import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import time
import threading
import os
import json


class Pomodoro:
    def __init__(self, root):
        self.root = root
        self.tasks = []
        self.current_task_index = -1
        self.timer_running = False
        self.timer_thread = None
        self.bg_image = None
        self.total_time_spent = 0  # Track total time spent on tasks

        # Load tasks from file if available
        self.load_tasks()

    def add_task(self):
        task_name = simpledialog.askstring("New Task", "Enter task name:")
        if task_name:
            try:
                time_limit = simpledialog.askinteger("Time Limit", "Enter time limit in minutes:")
                if time_limit is not None:
                    self.tasks.append((task_name, time_limit * 60))
                    self.update_task_list()
                    self.save_tasks()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number for the time limit.")

    def edit_task(self):
        selected_task = self.task_list.curselection()
        if selected_task:
            index = selected_task[0]
            task_name, time_limit = self.tasks[index]

            new_name = simpledialog.askstring("Edit Task", "Enter new task name:", initialvalue=task_name)
            if new_name:
                try:
                    new_time = simpledialog.askinteger(
                        "Edit Time Limit", "Enter new time limit in minutes:", initialvalue=time_limit // 60
                    )
                    if new_time is not None:
                        self.tasks[index] = (new_name, new_time * 60)
                        self.update_task_list()
                        self.save_tasks()
                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter a valid number for the time limit.")
        else:
            messagebox.showwarning("No Task Selected", "Please select a task to edit.")

    def update_task_list(self):
        self.task_list.delete(0, tk.END)
        for i, (task_name, _) in enumerate(self.tasks):
            self.task_list.insert(tk.END, f"{i + 1}. {task_name}")

    def start_task(self):
        selected_task = self.task_list.curselection()
        if selected_task:
            self.current_task_index = selected_task[0]
            task_name, time_limit = self.tasks[self.current_task_index]
            self.start_timer(time_limit, task_name)
        else:
            messagebox.showwarning("No Task Selected", "Please select a task to start.")

    def delete_task(self):
        selected_task = self.task_list.curselection()
        if selected_task:
            del self.tasks[selected_task[0]]
            self.update_task_list()
            self.save_tasks()
        else:
            messagebox.showwarning("No Task Selected", "Please select a task to delete.")

    def start_timer(self, duration, task_name):
        if not self.timer_running:
            self.timer_running = True
            self.timer_thread = threading.Thread(target=self.run_timer, args=(duration, task_name))
            self.timer_thread.start()

    def resume_task(self):
        if not self.timer_running and self.remaining_time > 0:
            if self.current_task_index != -1:
                task_name, _ = self.tasks[self.current_task_index]
                self.start_timer(self.remaining_time, task_name)
            else:
                messagebox.showwarning("No Task Selected", "No task to resume.")
        else:
            messagebox.showwarning("Timer Running", "The timer is already running or no task is paused.")

    def run_timer(self, duration, task_name):
        total_time = duration
        while duration >= 0 and self.timer_running:
            minutes, seconds = divmod(duration, 60)
            time_text = f"{minutes:02d}:{seconds:02d}"
            self.timer_canvas.itemconfig(self.timer_text, text=time_text)

            time_fraction = duration / total_time
            if time_fraction > 0.5:
                color = "#4CAF50"  # Green
            elif time_fraction > 0.2:
                color = "#FF9800"  # Orange
            else:
                color = "#f44336"  # Red

            self.timer_canvas.itemconfig(self.timer_circle, outline=color)
            self.root.update()
            time.sleep(1)
            duration -= 1

        if duration < 0 and self.timer_running:
            self.total_time_spent += total_time
            self.save_tasks()
            messagebox.showinfo("Task Complete", f"Task '{task_name}' completed!")
            self.start_break()

        self.timer_running = False

    def start_break(self):
        if messagebox.askyesno("Break Time", "Do you want to start a 5-minute break?"):
            self.start_timer(5 * 60, "Break")

    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False
            # Calculate remaining time
            current_text = self.timer_canvas.itemcget(self.timer_text, "text")
            minutes, seconds = map(int, current_text.split(":"))
            self.remaining_time = minutes * 60 + seconds
            messagebox.showinfo("Timer Stopped", f"Timer stopped with {minutes} minutes and {seconds} seconds remaining.")
        else:
            messagebox.showwarning("No Timer Running", "The timer is not running.")

    def save_tasks(self):
        with open("tasks.json", "w") as file:
            json.dump(self.tasks, file)

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                self.tasks = json.load(file)

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2 - radius, y2,
            x1 + radius, y2
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def main(self):
        self.root.attributes('-fullscreen', True)
        self.root.title("Enhanced Pomodoro Timer")
        self.root.configure(bg="#f0f0f0")

        self.canvas = tk.Canvas(self.root, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        try:
            img = Image.open("imagenew.jpeg").resize(
                (self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
            self.bg_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load background image: {e}")

        self.timer_canvas = tk.Canvas(self.root, width=250, height=250, bg="#f0f0f0", highlightthickness=0)
        self.timer_canvas.place(relx=0.5, rely=0.3, anchor="center")
        self.timer_circle = self.timer_canvas.create_oval(10, 10, 240, 240, outline="#FFA726", width=5)
        self.timer_text = self.timer_canvas.create_text(125, 125, text="25:00", font=("Arial", 40, "bold"), fill="#333")

        task_frame = tk.Frame(self.root, bg="white", bd=5, relief="ridge")
        task_frame.place(x=100, y=100, width=300, height=500)

        task_label = tk.Label(task_frame, text="Task List", font=("Arial", 16, "bold"), bg="white", fg="#333")
        task_label.pack(side="top", pady=5)
        self.task_list = tk.Listbox(task_frame, font=("Arial", 14), bg="#f9f9f9", fg="#333", bd=0, highlightthickness=0)
        self.task_list.pack(fill="both", expand=True, padx=5, pady=5)

        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.place(relx=0.5, rely=0.9, anchor="center")

        buttons = [
            {"text": "Add Task", "command": self.add_task},
            {"text": "Edit Task", "command": self.edit_task},
            {"text": "Start Task", "command": self.start_task},
            {"text": "Delete Task", "command": self.delete_task},
            {"text": "Resume Task", "command": self.resume_task},
            {"text": "Stop Timer", "command": self.stop_timer},
            {"text": "Exit", "command": self.root.destroy},
        ]

        for idx, btn in enumerate(buttons):
            btn_canvas = tk.Canvas(button_frame, width=120, height=50, bg="#f0f0f0", highlightthickness=0)
            btn_canvas.grid(row=0, column=idx, padx=10, pady=10)
            # Create the rounded rectangle and store its ID
            rect_id = btn_canvas.create_rectangle(10, 10, 110, 40, fill="#A9D2EB", outline="#A9D2EB")
            # Create the text and store its ID
            text_id = btn_canvas.create_text(60, 25, text=btn["text"], fill="#333", font=("Arial", 12, "bold"))
            # Bind both rectangle and text to the command
            btn_canvas.tag_bind(rect_id, "<Button-1>", lambda e, cmd=btn["command"]: cmd())
            btn_canvas.tag_bind(text_id, "<Button-1>", lambda e, cmd=btn["command"]: cmd())


        self.update_task_list()
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    pomo = Pomodoro(root)
    pomo.main()
