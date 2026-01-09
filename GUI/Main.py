import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib
from datetime import date, datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import mplcursors
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from PIL import Image, ImageTk


# ---------------- CONFIG ---------------- #

USER_FILE = "users.json"

GRADE_CONVERSION = {"VB": 0} | {f"V{i}": i for i in range(18)}

STYLES = ["Powerful", "Slopey", "Crimpy", "Technical", "Dynamic"]

# ---------------- UTILITIES ---------------- #

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def convert_to_v_grade(grade):
    grade = grade.strip().upper()
    if grade.startswith("V") and grade[1:].isdigit():
        return int(grade[1:])
    if grade in GRADE_CONVERSION:
        return GRADE_CONVERSION[grade]
    raise ValueError("Unknown grade format")

# ---------------- MAIN APP ---------------- #

class BelayBuddy:
    def __init__(self, root):
        self.root = root
        self.root.title("Belay Buddy")
        self.current_user = None
        self.users = load_users()
        self.show_start_screen()

    # ---------- START SCREEN ---------- #

    def show_start_screen(self):
        self.clear()

        logo_img = Image.open(r"Assets\Logo.png")
        logo_img = logo_img.resize((400, 200))

        self.logo = ImageTk.PhotoImage(logo_img)
        self.logo_label = tk.Label(self.root, image=self.logo)
        self.logo_label.pack(pady=20)

        tk.Button(self.root, text="Login", width=20, command=self.show_login).pack(pady=1)
        tk.Button(self.root, text="Create New Account", width=20, command=self.show_create_account).pack(pady=1)
        tk.Button(self.root, text="User Guide", width=20, command=self.guide).pack(pady=1)
        tk.Button(self.root, text="Exit App", width=20, command=self.exit).pack(pady=1)

    # ---------- CREATE ACCOUNT ---------- #

    def show_create_account(self):
        self.clear()

        tk.Label(self.root, text="Create Account", font=("Arial", 18)).pack(pady=10)

        self.ca_name = tk.Entry(self.root)
        self.ca_username = tk.Entry(self.root)
        self.ca_password = tk.Entry(self.root, show="*")

        tk.Label(self.root, text="Full Name").pack()
        self.ca_name.pack()

        tk.Label(self.root, text="Username").pack()
        self.ca_username.pack()

        tk.Label(self.root, text="Password").pack()
        self.ca_password.pack()

        tk.Label(self.root, text="Account Type").pack()
        self.ca_type = ttk.Combobox(self.root, values=["Climber", "Routesetter"], state="readonly")
        self.ca_type.pack()

        tk.Button(self.root, text="Create", command=self.create_account).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_start_screen).pack()

    def create_account(self):
        name = self.ca_name.get()
        username = self.ca_username.get()
        password = self.ca_password.get()
        acc_type = self.ca_type.get()

        if not all([name, username, password, acc_type]):
            messagebox.showerror("Error", "All fields required")
            return

        if username in self.users:
            messagebox.showerror("Error", "Username already exists")
            return

        self.users[username] = {
            "name": name,
            "password": hash_password(password),
            "type": acc_type,
            "climbs": []
        }

        save_users(self.users)
        messagebox.showinfo("Success", "Account created")
        self.show_start_screen()

    def guide(self):
        self.clear()
        tk.Button(self.root, text="Back", command=self.show_start_screen).pack()

    def exit(self):
        self.root.destroy()

    # ---------- LOGIN ---------- #

    def show_login(self):
        self.clear()

        tk.Label(self.root, text="Login", font=("Arial", 18)).pack(pady=10)

        self.lg_username = tk.Entry(self.root)
        self.lg_password = tk.Entry(self.root, show="*")

        tk.Label(self.root, text="Username").pack()
        self.lg_username.pack()

        tk.Label(self.root, text="Password").pack()
        self.lg_password.pack()

        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_start_screen).pack()

    def login(self):
        username = self.lg_username.get()
        password = self.lg_password.get()

        if username not in self.users:
            messagebox.showerror("Error", "Invalid login")
            return

        if self.users[username]["password"] != hash_password(password):
            messagebox.showerror("Error", "Invalid login")
            return

        self.current_user = username
        self.show_home()

    # ---------- HOME ---------- #

    def show_home(self):
        self.clear()

        tk.Label(self.root, text=f"Welcome {self.users[self.current_user]['name']}",
                 font=("Arial", 16)).pack(pady=10)

        tk.Button(self.root, text="Log Climb", command=self.show_log_climb).pack(pady=5)
        tk.Button(self.root, text="Refresh Graph", command=self.plot_graph).pack()

        self.plot_graph()

    def plot_graph(self):
        # Clear old graph if it exists
        if hasattr(self, "graph_canvas"):
            self.graph_canvas.get_tk_widget().destroy()

        climbs = self.users[self.current_user]["climbs"]
        if len(climbs) == 0:
            return

        dates = [datetime.strptime(c["date"], "%Y-%m-%d") for c in climbs]
        base_date = min(dates)
        x = np.array([(d - base_date).days for d in dates], dtype=float) #https://stackoverflow.com/questions/9627686/plotting-dates-on-the-x-axis

        for i in range(len(x)):
            x[i] += 0.05 * (x[:i] == x[i]).sum()

        y = np.array([c["v_grade"] for c in climbs], dtype=float)

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)

        scatter = ax.scatter(x, y)

        if len(y) >= 3:
            degree = 2
        elif len(y) == 2:
            degree = 1
        else:
            degree = None

        if degree is not None:
            coeffs = np.polyfit(x, y, degree)
            poly = np.poly1d(coeffs)
            xs = np.linspace(min(x), max(x), 200)
            ax.plot(xs, poly(xs))

        ax.set_xlabel("Date")
        ax.set_ylabel("V Grade")
        ax.set_title("Climbing Progress")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, alpha=0.3)

        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(pady=10)

        cursor = mplcursors.cursor(scatter, hover=True)

        @cursor.connect("add")
        def on_add(sel):
            climb = climbs[sel.index]
            sel.annotation.set_text(
                f"Route: {climb['route']}\n"
                f"Grade: V{climb['v_grade']}\n"
                f"Date: {climb['date']}\n"
                f"Style: {climb.get('style', '')}\n"
                f"Gym: {climb.get('gym', '')}\n"
                "[Right-CLick To Close]"
            )
            sel.annotation.get_bbox_patch().set(alpha=0.85)

        @cursor.connect("remove")
        def on_remove(sel):
            sel.annotation.set_visible(False)

    # ---------- LOG CLIMB ---------- #

    def show_log_climb(self):
        win = tk.Toplevel(self.root)
        win.title("Log Climb")

        tk.Label(win, text="Route Type").pack()
        route_type = ttk.Combobox(win, values=["Existing Route", "Custom"], state="readonly")
        route_type.pack()

        tk.Label(win, text="Route Name").pack()
        route_name = tk.Entry(win)
        route_name.pack()

        tk.Label(win, text="Grade").pack()
        grade_entry = tk.Entry(win)
        grade_entry.pack()

        tk.Label(win, text="Style (optional)").pack()
        style_box = ttk.Combobox(win, values=STYLES)
        style_box.pack()

        tk.Label(win, text="Gym (optional)").pack()
        gym_entry = tk.Entry(win)
        gym_entry.pack()

        tk.Label(win, text="Date (YYYY-MM-DD)").pack()
        date_entry = tk.Entry(win)
        date_entry.pack()

        def save_climb():
            try:
                v_grade = convert_to_v_grade(grade_entry.get())
            except:
                messagebox.showerror("Error", "Invalid grade")
                return

            climb_date = date_entry.get() or date.today().isoformat()

            gym = gym_entry.get()
            if gym == "":
                gym = "N/A"

            style = style_box.get()
            if style == "":
                style = "N/A"


            self.users[self.current_user]["climbs"].append({
                "route": route_name.get() or "Custom",
                "v_grade": v_grade,
                "style": style,
                "gym": gym,
                "date": climb_date
            })

            save_users(self.users)
            win.destroy()
            self.plot_graph()

        tk.Button(win, text="Save", command=save_climb).pack(pady=10)

    # ---------- UTILS ---------- #

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x400")
    root.configure(background='white')
    app = BelayBuddy(root)
    root.mainloop()
