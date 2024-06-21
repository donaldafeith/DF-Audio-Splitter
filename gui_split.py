import os
import warnings
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import multiprocessing
import time

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

def split_audio_process(input_file, output_directory, num_stems, progress_queue):
    from spleeter.separator import Separator

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    model_map = {
        2: 'spleeter:2stems',
        3: 'spleeter:3stems',
        4: 'spleeter:4stems',
        5: 'spleeter:5stems'
    }
    
    separator = Separator(model_map[num_stems])
    
    progress_queue.put(20)
    
    separator.separate_to_file(input_file, output_directory)
    
    progress_queue.put(80)

    track_name_map = {
        2: ['vocals', 'accompaniment'],
        3: ['vocals', 'drums', 'other'],
        4: ['vocals', 'drums', 'bass', 'other'],
        5: ['vocals', 'drums', 'bass', 'piano', 'other']
    }
    track_names = track_name_map[num_stems]
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    for track in track_names:
        src = os.path.join(output_directory, base_name, track + '.wav')
        dst = os.path.join(output_directory, base_name + '_' + track + '.wav')
        if os.path.exists(src):
            os.rename(src, dst)

    progress_queue.put(100)
    progress_queue.put("done")

class AudioSplitterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Audio Splitter")

        # Input file selection
        tk.Label(master, text="Select audio file:").grid(row=0, column=0, padx=10, pady=10)
        self.file_entry = tk.Entry(master, width=50)
        self.file_entry.grid(row=0, column=1, padx=10, pady=10)
        file_button = tk.Button(master, text="Browse...", command=self.select_file)
        file_button.grid(row=0, column=2, padx=10, pady=10)

        # Output directory selection
        tk.Label(master, text="Select output directory:").grid(row=1, column=0, padx=10, pady=10)
        self.output_entry = tk.Entry(master, width=50)
        self.output_entry.grid(row=1, column=1, padx=10, pady=10)
        output_button = tk.Button(master, text="Browse...", command=self.select_output_directory)
        output_button.grid(row=1, column=2, padx=10, pady=10)

        # Number of stems input
        tk.Label(master, text="Number of stems (2, 3, 4, 5):").grid(row=2, column=0, padx=10, pady=10)
        self.stems_entry = tk.Entry(master, width=5)
        self.stems_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(master, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=20, sticky='ew')

        # Start button
        self.start_button = tk.Button(master, text="Start Splitting", command=self.start_splitting)
        self.start_button.grid(row=4, column=0, columnspan=3, pady=20)

        self.process = None
        self.progress_queue = multiprocessing.Queue()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.m4a *.wma")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def select_output_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, directory_path)

    def start_splitting(self):
        input_file = self.file_entry.get()
        output_directory = self.output_entry.get()
        try:
            num_stems = int(self.stems_entry.get())
            if num_stems not in [2, 3, 4, 5]:
                raise ValueError
            self.progress_var.set(0)
            self.start_button.config(state=tk.DISABLED)
            self.process = multiprocessing.Process(target=split_audio_process, 
                                                   args=(input_file, output_directory, num_stems, self.progress_queue))
            self.process.start()
            self.master.after(100, self.check_progress)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of stems (2, 3, 4, or 5).")

    def check_progress(self):
        try:
            while True:
                progress = self.progress_queue.get_nowait()
                if progress == "done":
                    messagebox.showinfo("Success", f"Tracks have been saved in {self.output_entry.get()}")
                    self.start_button.config(state=tk.NORMAL)
                    return
                else:
                    self.progress_var.set(progress)
        except:
            pass
        finally:
            self.master.after(100, self.check_progress)

if __name__ == "__main__":
    root = tk.Tk()
    gui = AudioSplitterGUI(root)
    root.mainloop()