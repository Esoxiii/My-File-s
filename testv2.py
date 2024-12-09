import os
import re
import time
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import csv


minecraft_folder = os.path.expanduser("~/.minecraft")  # Zmienna zależna od systemu
logs_folder = os.path.join(minecraft_folder, "logs")
latest_log_file = os.path.join(logs_folder, "latest.log")
user_folder = os.path.expanduser("~")  # Folder użytkownika
output_file = "detected_cheats_and_mods.csv"  # Domyślny plik wyników


cheat_keywords = [
    "cheat", "xray", "fly", "aimbot", "speedhack", "hacked", "hax", "mod", "ghostclient", "nofall", "forcefield", "triggerbot",
    "kill aura", "autosprint", "autojump", "bhop", "velocity", "flyhack", "chams", "esp", "wallhack", "autowalk"
]


def find_jar_files_in_folder(path):
    jar_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".jar"):
                file_path = os.path.join(root, file)
                jar_files.append(file_path)
    return jar_files


def find_cheats_in_logs(log_file):
    detected_cheats = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            log_data = f.read()
            for cheat in cheat_keywords:
                if re.search(cheat, log_data, re.IGNORECASE):
                    detected_cheats.append(cheat)
    return detected_cheats


def save_results_to_csv(jar_files, detected_cheats):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Wykryte pliki .jar"])
        for file in jar_files:
            writer.writerow([file])
        
        writer.writerow([])
        writer.writerow(["Wykryte cheaty w logach"])
        for cheat in detected_cheats:
            writer.writerow([cheat])

    print(f"Zapisano wyniki do {output_file}")


def estimate_time(start_time, processed_files, total_files):
    elapsed_time = time.time() - start_time
    if processed_files > 0:
        remaining_files = total_files - processed_files
        time_per_file = elapsed_time / processed_files
        estimated_time_left = time_per_file * remaining_files
        return remaining_files, estimated_time_left
    return total_files, 0


def choose_output_folder():
    global output_file
    folder = filedialog.askdirectory()
    if folder:
        output_file = os.path.join(folder, "detected_cheats_and_mods.csv")


def start_scan():
    start_time = time.time()

    
    log_text.insert(tk.END, f"Szukam plików .jar w folderze użytkownika: {user_folder}\n")
    log_text.yview(tk.END)
    jar_files = find_jar_files_in_folder(user_folder)

    
    log_text.insert(tk.END, f"Sprawdzam logi Minecrafta w pliku: {latest_log_file}\n")
    log_text.yview(tk.END)
    detected_cheats = find_cheats_in_logs(latest_log_file)

    
    log_text.insert(tk.END, f"Szukam plików .jar w folderze Minecrafta: {minecraft_folder}\n")
    log_text.yview(tk.END)
    minecraft_jar_files = find_jar_files_in_folder(minecraft_folder)

    
    jar_files.extend(minecraft_jar_files)

    
    total_files = len(jar_files)
    processed_files = 0
    for _ in jar_files:
        processed_files += 1
        remaining_files, estimated_time_left = estimate_time(start_time, processed_files, total_files)
        progress['value'] = (processed_files / total_files) * 100
        window.update_idletasks()
        log_text.insert(tk.END, f"Pozostało {remaining_files} plików, szacowany czas do końca: {estimated_time_left:.2f} sekund\n")
        log_text.yview(tk.END)

    
    if jar_files or detected_cheats:
        save_results_to_csv(jar_files, detected_cheats)
    else:
        log_text.insert(tk.END, "Nie znaleziono żadnych podejrzanych plików .jar ani cheatów w logach.\n")
        log_text.yview(tk.END)

    
    total_time = time.time() - start_time
    log_text.insert(tk.END, f"Skanowanie zakończone. Czas trwania: {total_time:.2f} sekund.\n")
    log_text.yview(tk.END)
    messagebox.showinfo("Zakończono", "Skanowanie zakończone. Zapisano wyniki.")
    
    
    window.bell()


def create_gui():
    global window, log_text, progress, output_file

    
    window = tk.Tk()
    window.title("Minecraft Cheat Detector")
    window.geometry("600x400")

    
    title_label = tk.Label(window, text="Skanowanie w poszukiwaniu cheatów w Minecraft", font=("Arial", 14))
    title_label.pack(pady=10)

    
    scan_button = tk.Button(window, text="Rozpocznij skanowanie", command=start_scan, font=("Arial", 12), bg="green", fg="white")
    scan_button.pack(pady=10)

    
    choose_folder_button = tk.Button(window, text="Wybierz folder wyników", command=choose_output_folder, font=("Arial", 12))
    choose_folder_button.pack(pady=10)

    
    progress = ttk.Progressbar(window, length=500, mode="determinate", maximum=100)
    progress.pack(pady=10)

    
    log_text = tk.Text(window, height=10, width=70)
    log_text.pack(pady=10)
    log_text.insert(tk.END, "Wyniki skanowania będą wyświetlane tutaj...\n")

    
    window.mainloop()


create_gui()
