import os
import zipfile
import py7zr
import rarfile
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import Button, Label
from tkinter.ttk import Progressbar
from threading import Thread
import time
import re

# Lista nazw cheatów i modów
hack_clients = ['xray', 'cheat', 'hack', 'client', 'aimbot', 'wallhack', 'autoclicker', 'speedhack', 
                'flyhack', 'triggerbot', 'vape', 'esp', 'blaze', 'viper', 'apex', 'rogue', 'spectre', 
                'vortex', 'shadow', 'tornado', 'echo', 'cyclone', 'phoenix', 'titan', 'inferno']

# Globalna lista wyników skanowania
scan_results = []

# Funkcja do zapisywania wyników do pliku tekstowego
def save_results_to_file():
    with open("scan_results.txt", "w", encoding="utf-8") as file:
        for result in scan_results:
            file.write(result + "\n")

# Funkcja do dodawania wyników do listy
def add_scan_result(result):
    scan_results.append(result)

# Funkcja do sprawdzania, czy plik zawiera podejrzaną nazwę
def is_suspect_file(file_path):
    return any(hack_client in file_path.lower() for hack_client in hack_clients)

# Funkcja do sprawdzania, czy plik JAR jest podejrzany (analiza zawartości)
def is_suspect_jar(file_path):
    try:
        with zipfile.ZipFile(file_path, 'r') as jar:
            for file in jar.namelist():
                # Sprawdzamy czy plik w .jar zawiera podejrzane klasy
                if any(hack_client in file.lower() for hack_client in hack_clients):
                    return True
    except zipfile.BadZipFile:
        return False  # Niepoprawny plik .jar
    return False

# Funkcja do sprawdzania, czy paczka tekstur zawiera "xray"
def check_for_xray_texture(resourcepack_folder):
    for root, dirs, files in os.walk(resourcepack_folder):
        for file in files:
            if 'xray' in file.lower():  # Możemy szukać plików z nazwą zawierającą 'xray'
                return True
    return False

# Funkcja do skanowania plików w folderach z wielowątkowością
def scan_files_in_folder(folder_path, text_widget, progress_bar, quick_scan, start_time, update_progress, update_time, update_remaining_time):
    file_count = 0
    total_files = sum([len(files) for _, _, files in os.walk(folder_path)])
    current_file = 0
    start_scan_time = time.time()

    def scan_files():
        nonlocal current_file, start_scan_time
        total_files = sum([len(files) for _, _, files in os.walk(folder_path)])  # Ponowne obliczenie, by być pewnym, że total_files jest prawidłowe
        elapsed_time = time.time() - start_scan_time
        avg_time_per_file = elapsed_time / (current_file if current_file > 0 else 1)
        remaining_files = total_files - current_file
        remaining_time = remaining_files * avg_time_per_file
        remaining_minutes = int(remaining_time // 60)
        remaining_seconds = int(remaining_time % 60)

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                current_file += 1

                # Jeśli jest to szybkie skanowanie, sprawdzamy tylko pliki .jar i .exe
                if quick_scan and file.lower().endswith(('.jar', '.exe')):
                    if is_suspect_file(file_path):
                        result = f"Znaleziono podejrzany plik: {file_path}"
                        add_scan_result(result)
                        text_widget.insert(tk.END, result + "\n")

                    # Dodatkowe sprawdzenie, czy plik JAR jest podejrzany
                    elif file.lower().endswith('.jar') and is_suspect_jar(file_path):
                        result = f"Znaleziono podejrzany plik JAR: {file_path}"
                        add_scan_result(result)
                        text_widget.insert(tk.END, result + "\n")
                
                # Jeśli to pełne skanowanie, sprawdzamy wszystkie pliki
                elif not quick_scan:
                    if is_suspect_file(file_path):
                        result = f"Znaleziono podejrzany plik: {file_path}"
                        add_scan_result(result)
                        text_widget.insert(tk.END, result + "\n")
                
                # Sprawdzanie archiwów tylko, jeśli to pełne skanowanie
                if not quick_scan and file.lower().endswith(('.zip', '.rar', '.7z', '.tar')): 
                    try:
                        if file.lower().endswith('.zip'):
                            with zipfile.ZipFile(file_path, 'r') as archive:
                                for f in archive.namelist():
                                    if is_suspect_file(f):
                                        result = f"Znaleziono podejrzany plik w archiwum ZIP: {f}"
                                        add_scan_result(result)
                                        text_widget.insert(tk.END, result + "\n")
                        elif file.lower().endswith('.rar'):
                            with rarfile.RarFile(file_path, 'r') as archive:
                                for f in archive.namelist():
                                    if is_suspect_file(f):
                                        result = f"Znaleziono podejrzany plik w archiwum RAR: {f}"
                                        add_scan_result(result)
                                        text_widget.insert(tk.END, result + "\n")
                        elif file.lower().endswith('.7z'):
                            with py7zr.SevenZipFile(file_path, mode='r') as archive:
                                for f in archive.getnames():
                                    if is_suspect_file(f):
                                        result = f"Znaleziono podejrzany plik w archiwum 7z: {f}"
                                        add_scan_result(result)
                                        text_widget.insert(tk.END, result + "\n")
                    except Exception as e:
                        result = f"Błąd przy otwieraniu pliku {file}: {str(e)}"
                        add_scan_result(result)
                        text_widget.insert(tk.END, result + "\n")

                # Aktualizowanie postępu i czasu
                update_progress(current_file, total_files)
                update_time(start_time)
                update_remaining_time(remaining_minutes, remaining_seconds)

        text_widget.insert(tk.END, f"Skanowanie folderu {folder_path} zakończone.\n")
        text_widget.yview(tk.END)

        # Zapisz wyniki po zakończeniu skanowania
        save_results_to_file()

    Thread(target=scan_files, daemon=True).start()  # Uruchamiamy skanowanie w osobnym wątku

# Funkcja do aktualizowania czasu skanowania
def update_time(start_time):
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    elapsed_label.config(text=f"Czas trwania: {minutes:02}:{seconds:02}")

# Funkcja do aktualizowania paska postępu
def update_progress(current_file, total_files):
    progress = (current_file / total_files) * 100
    progress_bar['value'] = progress
    progress_bar.update_idletasks()

# Funkcja do aktualizowania czasu pozostałego
def update_remaining_time(remaining_minutes, remaining_seconds):
    remaining_time_label.config(text=f"Pozostały czas: {remaining_minutes:02}:{remaining_seconds:02}")

# Funkcja do uruchamiania pełnego skanowania (wielu lokalizacji)
def full_scan(text_widget, progress_bar, quick_scan_enabled):
    start_time = time.time()  # Rejestrujemy początek skanowania
    elapsed_label.config(text="Czas trwania: 00:00")  # Resetujemy czas
    remaining_time_label.config(text="Pozostały czas: 00:00")  # Resetujemy pozostały czas
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    documents = os.path.join(os.path.expanduser("~"), "Documents")
    pictures = os.path.join(os.path.expanduser("~"), "Pictures")
    music = os.path.join(os.path.expanduser("~"), "Music")
    videos = os.path.join(os.path.expanduser("~"), "Videos")
    appdata = os.path.join(os.getenv("APPDATA"))
    minecraft_folder = os.path.join(os.path.expanduser("~"), ".minecraft")

    # Skanowanie lokalnych folderów równolegle
    folders = [desktop, documents, pictures, music, videos, appdata]
    for folder in folders:
        scan_files_in_folder(folder, text_widget, progress_bar, quick_scan_enabled, start_time, update_progress, update_time, update_remaining_time)

    # Skanowanie Minecrafta równolegle
    if os.path.exists(minecraft_folder):
        scan_files_in_folder(minecraft_folder, text_widget, progress_bar, quick_scan_enabled, start_time, update_progress, update_time, update_remaining_time)

    # Zapisz wyniki do pliku po zakończeniu skanowania
    save_results_to_file()

# Inicjalizacja GUI
root = tk.Tk()
root.title("Skaner cheatów")

# GUI Setup
frame = tk.Frame(root, bg="lightblue")
frame.pack(pady=10)

label = Label(frame, text="Wybierz folder do skanowania:", bg="lightblue", font=("Helvetica", 12))
label.pack()

folder_button = Button(frame, text="Wybierz folder", command=lambda: scan_files_in_folder(filedialog.askdirectory(), text_widget, progress_bar, quick_scan_checkbox.get(), time.time(), update_progress, update_time, update_remaining_time), 
                       bg="green", fg="white", font=("Helvetica", 12))
folder_button.pack()

# Checkbox do wyboru szybkiego skanowania
quick_scan_checkbox = tk.BooleanVar(value=False)
quick_scan_checkbox_button = tk.Checkbutton(frame, text="Szybkie skanowanie", variable=quick_scan_checkbox, 
                                            bg="lightblue", font=("Helvetica", 12))
quick_scan_checkbox_button.pack()

full_scan_button = Button(frame, text="Inteligentne skanowanie", command=lambda: full_scan(text_widget, progress_bar, quick_scan_checkbox.get()), 
                          bg="blue", fg="white", font=("Helvetica", 12))
full_scan_button.pack()

# Etykieta z czasem trwania skanowania
elapsed_label = Label(frame, text="Czas trwania: 00:00", bg="lightblue", font=("Helvetica", 12))
elapsed_label.pack(pady=10)

# Etykieta z pozostałym czasem
remaining_time_label = Label(frame, text="Pozostały czas: 00:00", bg="lightblue", font=("Helvetica", 12))
remaining_time_label.pack(pady=10)

progress_bar = Progressbar(root, length=300, mode='determinate')
progress_bar.pack(pady=20)

text_widget = scrolledtext.ScrolledText(root, width=80, height=20, font=("Courier", 10), wrap=tk.WORD)
text_widget.pack(padx=10, pady=10)

root.mainloop()
