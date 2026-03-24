import sys
import tkinter as tk
from tkinter import scrolledtext
import main  # Imports your existing main.py

class RedirectText(object):
    """Redirects console print statements to the GUI text box"""
    def __init__(self, text_ctrl):
        self.output = text_ctrl
    def write(self, string):
        self.output.insert(tk.END, string)
        self.output.see(tk.END)
    def flush(self):
        pass

def create_gui():
    window = tk.Tk()
    window.title("ITL351: Network Simulator")
    window.geometry("800x600")
    window.configure(bg="#2b2b2b") # Sleek dark mode background

    # Title Label
    title = tk.Label(window, text="Network Simulator Control Panel", font=("Helvetica", 16, "bold"), bg="#2b2b2b", fg="white")
    title.pack(pady=10)

    # Output Screen
    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=90, height=25, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
    text_area.pack(pady=10)

    # Redirect standard output to the text area
    sys.stdout = RedirectText(text_area)

    # Button Frame
    btn_frame = tk.Frame(window, bg="#2b2b2b")
    btn_frame.pack(pady=10)

    # Buttons to trigger your exact test cases
    btn1 = tk.Button(btn_frame, text="Run Test Case 1", command=main.run_test_case_1, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
    btn1.grid(row=0, column=0, padx=10)

    btn2 = tk.Button(btn_frame, text="Run Test Case 2", command=main.run_test_case_2, bg="#2196F3", fg="white", font=("Helvetica", 10, "bold"))
    btn2.grid(row=0, column=1, padx=10)

    btn3 = tk.Button(btn_frame, text="Run Test Case 3", command=main.run_test_case_3, bg="#FF9800", fg="white", font=("Helvetica", 10, "bold"))
    btn3.grid(row=0, column=2, padx=10)

    btn4 = tk.Button(btn_frame, text="Run Test Case 4", command=main.run_test_case_4, bg="#9C27B0", fg="white", font=("Helvetica", 10, "bold"))
    btn4.grid(row=0, column=3, padx=10)

    window.mainloop()

if __name__ == "__main__":
    create_gui()