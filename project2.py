import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import smtplib
from email.message import EmailMessage
from collections import defaultdict

# -------------------------------------------------------------------
# Data Setup
# -------------------------------------------------------------------
# Create a dictionary for 10 students with both their student and parent's emails.
students_info = {
    f"Student {i+1}": {
        "student_email": f"student{i+1}@example.com",
        "parent_email": f"parent{i+1}@example.com"
    } for i in range(10)
}

# Create a dictionary (defaultdict) to store tasks for each student.
# Each task is represented as a dictionary with a name and a status.
tasks = defaultdict(list)
for student in students_info:
    tasks[student] = []

# -------------------------------------------------------------------
# Functions for Task Operations
# -------------------------------------------------------------------
def add_task():
    """Create a new task and assign it to the selected student."""
    task_name = simpledialog.askstring("New Task", "Enter task name:")
    if not task_name:
        return

    # For simplicity, ask the counsellor to type the status.
    task_status = simpledialog.askstring("Task Status", "Enter status (Pending, In Progress, Completed):")
    if task_status not in ["Pending", "In Progress", "Completed"]:
        messagebox.showerror("Error", "Invalid status! Please enter: Pending, In Progress, or Completed.")
        return

    student = student_var.get()
    tasks[student].append({"name": task_name, "status": task_status})
    messagebox.showinfo("Success", f"Task '{task_name}' added for {student}.")
    refresh_task_list()

def update_task_status():
    """Update the status of the selected task for the current student."""
    student = student_var.get()
    selected = task_listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a task to update.")
        return
    index = selected[0]
    current_task = tasks[student][index]
    new_status = simpledialog.askstring(
        "Update Task Status",
        f"Update status for '{current_task['name']}' (Pending, In Progress, Completed):"
    )
    if new_status not in ["Pending", "In Progress", "Completed"]:
        messagebox.showerror("Error", "Invalid status! Please enter: Pending, In Progress, or Completed.")
        return
    current_task['status'] = new_status
    messagebox.showinfo("Updated", f"Task '{current_task['name']}' updated to {new_status}.")
    refresh_task_list()

def refresh_task_list(*args):
    """Refresh the listbox to show tasks for the selected student."""
    student = student_var.get()
    task_listbox.delete(0, tk.END)
    for task in tasks[student]:
        task_listbox.insert(tk.END, f"{task['name']} - {task['status']}")

def show_aggregated_results():
    """Show aggregated statistics: total tasks, count by status."""
    total_tasks = sum(len(tlist) for tlist in tasks.values())
    pending = sum(task['status'] == "Pending" for tlist in tasks.values() for task in tlist)
    in_progress = sum(task['status'] == "In Progress" for tlist in tasks.values() for task in tlist)
    completed = sum(task['status'] == "Completed" for tlist in tasks.values() for task in tlist)
    stats = (
        f"Total Tasks: {total_tasks}\n"
        f"Pending: {pending}\n"
        f"In Progress: {in_progress}\n"
        f"Completed: {completed}"
    )
    messagebox.showinfo("Aggregated Results", stats)

# -------------------------------------------------------------------
# Email Functionality
# -------------------------------------------------------------------
def email_task():
    """
    Email the details of the selected task to the student and their parent.
    
    This function builds an email message (using EmailMessage) that includes
    the task details and sends it using Gmail's SMTP server. (Remember to replace
    'your_email@gmail.com' and 'your_app_password' with your actual credentials.)
    """
    student = student_var.get()
    selected = task_listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a task to email.")
        return
    index = selected[0]
    task = tasks[student][index]

    subject = f"New Task Assigned: {task['name']}"
    body = (
        f"Hello {student},\n\n"
        f"You have been assigned a new task:\n"
        f"Task: {task['name']}\n"
        f"Status: {task['status']}\n\n"
        f"Please log into your portal for further details and to update your progress.\n\n"
        f"Best regards,\n"
        f"Your Counsellor"
    )

    # Retrieve emails from our students_info dictionary.
    student_email = students_info[student]["student_email"]
    parent_email = students_info[student]["parent_email"]
    recipients = [student_email, parent_email]

    # Sender email credentials (replace with your own or load securely)
    sender_email = "your_email@gmail.com"       # Your sender email address
    sender_password = "your_app_password"         # Your app password if using 2FA

    # Build the email message.
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients)
    msg.set_content(body)

    # Send the email.
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        messagebox.showinfo("Email Sent", f"Email sent to {student_email} and {parent_email}.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {e}")

# -------------------------------------------------------------------
# Build the GUI with Tkinter
# -------------------------------------------------------------------
root = tk.Tk()
root.title("EduTask Manager - Student Counsellor To-Do App")
root.geometry("800x600")

# Student selection dropdown (using the keys of students_info)
student_var = tk.StringVar(value=list(students_info.keys())[0])
student_menu = ttk.OptionMenu(root, student_var, list(students_info.keys())[0], *students_info.keys(), command=refresh_task_list)
student_menu.pack(pady=10)

# Listbox to display tasks for the selected student
task_listbox = tk.Listbox(root, width=80, height=15)
task_listbox.pack(pady=10)

# Frame for action buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="Add Task", command=add_task, width=15)
add_button.grid(row=0, column=0, padx=5)

update_button = tk.Button(button_frame, text="Update Task", command=update_task_status, width=15)
update_button.grid(row=0, column=1, padx=5)

aggregated_button = tk.Button(button_frame, text="Aggregated Results", command=show_aggregated_results, width=18)
aggregated_button.grid(row=0, column=2, padx=5)

email_button = tk.Button(button_frame, text="Email Task", command=email_task, width=15)
email_button.grid(row=0, column=3, padx=5)

# Initially load tasks for the first student
refresh_task_list()

root.mainloop()