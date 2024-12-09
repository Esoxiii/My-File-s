import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import time
import os
import threading  # Importujemy threading

# Ścieżki do folderów Minecrafta
minecraft_folder = os.path.expanduser("~/.minecraft")  # Zmienna zależna od systemu
logs_folder = os.path.join(minecraft_folder, "logs")
latest_log_file = os.path.join(logs_folder, "latest.log")
user_folder = os.path.expanduser("~")  # Folder użytkownika
downloads_folder = os.path.join(user_folder, "Downloads")  # Domyślny folder Pobrane

# Globalne zmienne
scan_running = False
output_file = "detected_cheats_and_mods.txt"

# Funkcja do znalezienia plików .jar w folderze
def find_jar_files_in_folder(path):
    jar_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".jar"):
                file_path = os.path.join(root, file)
                jar_files.append(file_path)
    return jar_files

# Funkcja do znalezienia cheatów w logach Minecrafta
def find_cheats_in_logs(log_file):
    detected_cheats = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            log_data = f.read()
            # Przykładowe frazy, które mogą wskazywać na cheaty
            cheat_keywords = ["cheat", "xray", "fly", "aimbot", "speedhack", "hacked", "hax"]
            for cheat in cheat_keywords:
                if cheat.lower() in log_data.lower():
                    detected_cheats.append(cheat)
    return detected_cheats

# Funkcja do znalezienia cheatów w folderze pobranych plików (Downloads)
def find_cheats_in_downloads(path):
    cheat_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".jar") or file.endswith(".zip"):  # Możliwe cheaty w tych formatach
                file_path = os.path.join(root, file)
                cheat_files.append(file_path)
    return cheat_files

# Funkcja do znalezienia modów w folderze
def find_mods_in_folder(path):
    mods = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".jar") or file.endswith(".zip"):  # Moduły zwykle mają takie rozszerzenia
                file_path = os.path.join(root, file)
                mods.append(file_path)
    return mods

# Funkcja do znalezienia paczek tekstur w folderze
def find_texture_packs(path):
    texture_packs = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".zip"):  # Paczki tekstur zwykle są w formacie .zip
                file_path = os.path.join(root, file)
                texture_packs.append(file_path)
    return texture_packs

# Funkcja do zapisu wyników do pliku .txt
def save_results_to_txt(jar_files, detected_cheats, mods, texture_packs, download_cheats):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Wykryte pliki .jar:\n")
        for file in jar_files:
            f.write(file + "\n")
        
        f.write("\nWykryte cheaty w logach:\n")
        for cheat in detected_cheats:
            f.write(cheat + "\n")
        
        f.write("\nWykryte mody:\n")
        for mod in mods:
            f.write(mod + "\n")
        
        f.write("\nWykryte paczki tekstur:\n")
        for texture in texture_packs:
            f.write(texture + "\n")

        f.write("\nWykryte pliki cheatu w folderze Pobrane:\n")
        for cheat in download_cheats:
            f.write(cheat + "\n")

    print(f"Zapisano wyniki do {output_file}")

# Funkcja do estymacji pozostałego czasu skanowania
def estimate_time(start_time, processed_files, total_files):
    elapsed_time = time.time() - start_time
    if processed_files > 0:
        remaining_files = total_files - processed_files
        time_per_file = elapsed_time / processed_files
        estimated_time_left = time_per_file * remaining_files
        return remaining_files, estimated_time_left
    return total_files, 0

# Funkcja do rozpoczęcia skanowania
def start_scan():
    global scan_running, output_file
    scan_running = True
    start_time = time.time()

    jar_files = []
    detected_cheats = []
    mods = []
    texture_packs = []
    download_cheats = []

    # Skanowanie plików .jar
    if scan_jar.get():
        log_text.insert(tk.END, f"Szukam plików .jar w folderze użytkownika: {user_folder}\n")
        log_text.yview(tk.END)
        jar_files = find_jar_files_in_folder(user_folder)

        log_text.insert(tk.END, f"Szukam plików .jar w folderze Minecrafta: {minecraft_folder}\n")
        log_text.yview(tk.END)
        jar_files.extend(find_jar_files_in_folder(minecraft_folder))

    # Skanowanie logów Minecrafta
    if scan_logs.get():
        log_text.insert(tk.END, f"Sprawdzam logi Minecrafta w pliku: {latest_log_file}\n")
        log_text.yview(tk.END)
        detected_cheats = find_cheats_in_logs(latest_log_file)

    # Skanowanie modów
    if scan_mods.get():
        log_text.insert(tk.END, f"Szukam modów w folderze mods\n")
        log_text.yview(tk.END)
        mods = find_mods_in_folder(os.path.join(minecraft_folder, "mods"))

    # Skanowanie paczek tekstur
    if scan_texture_packs.get():
        log_text.insert(tk.END, f"Szukam paczek tekstur w folderze resourcepacks\n")
        log_text.yview(tk.END)
        texture_packs = find_texture_packs(os.path.join(minecraft_folder, "resourcepacks"))

    # Skanowanie pobranych cheatów z przeglądarki
    if scan_download_cheats.get():
        log_text.insert(tk.END, f"Szukam cheatów w folderze Pobrane: {downloads_folder}\n")
        log_text.yview(tk.END)
        download_cheats = find_cheats_in_downloads(downloads_folder)

    # Liczba plików do przetworzenia
    total_files = len(jar_files) + len(mods) + len(texture_packs) + len(download_cheats)
    processed_files = 0

    if total_files == 0:
        log_text.insert(tk.END, "Nie znaleziono żadnych plików do przetworzenia.\n")
        log_text.yview(tk.END)

    # Liczenie plików
    for file in jar_files + mods + texture_packs + download_cheats:
        if not scan_running:
            break
        processed_files += 1
        remaining_files, estimated_time_left = estimate_time(start_time, processed_files, total_files)
        progress['value'] = (processed_files / total_files) * 100
        window.update_idletasks()
        log_text.insert(tk.END, f"Pozostało {remaining_files} plików, szacowany czas do końca: {estimated_time_left:.2f} sekund\n")
        log_text.yview(tk.END)

    if scan_running:
        save_results_to_txt(jar_files, detected_cheats, mods, texture_packs, download_cheats)
        log_text.insert(tk.END, "Skanowanie zakończone.\n")
        messagebox.showinfo("Zakończono", "Skanowanie zakończone. Zapisano wyniki.")
    else:
        log_text.insert(tk.END, "Skanowanie przerwane.\n")

    total_time = time.time() - start_time
    log_text.insert(tk.END, f"Czas trwania: {total_time:.2f} sekund.\n")
    log_text.yview(tk.END)

# Funkcja do utworzenia GUI
def create_gui():
    global window, log_text, progress, scan_running, scan_jar, scan_logs, scan_mods, scan_texture_packs, scan_download_cheats

    window = tk.Tk()
    window.title("Minecraft Cheat Detector")
    window.geometry("900x600")  # Zwiększona przestronność
    window.config(bg="#1e1e1e")  # Ciemne tło

    scan_running = False

    # Ustawienie czcionki i kolorów
    font_style = ("Arial", 12)
    button_font = ("Arial", 12, "bold")

    # Ramka kontrolna
    control_frame = tk.Frame(window, bg="#2e3e46", bd=10, relief="solid")
    control_frame.pack(fill="x", padx=20, pady=10)

    title_label = tk.Label(control_frame, text="Minecraft Cheat Detector", font=("Arial", 18, "bold"), fg="white", bg="#2e3e46")
    title_label.pack(pady=10)

    # Przełączniki opcji
    scan_jar = tk.BooleanVar(value=True)
    scan_logs = tk.BooleanVar(value=True)
    scan_mods = tk.BooleanVar(value=True)
    scan_texture_packs = tk.BooleanVar(value=True)
    scan_download_cheats = tk.BooleanVar(value=True)

    # Stwórz przyciski przełączające dla różnych opcji
    options_frame = tk.Frame(control_frame, bg="#2e3e46")
    options_frame.pack()

    jar_button = tk.Checkbutton(options_frame, text="Szukaj plików .jar", variable=scan_jar, font=button_font, fg="white", bg="#2e3e46", selectcolor="#3d3d3d", activebackground="#3d3d3d")
    jar_button.grid(row=0, column=0, padx=5)

    logs_button = tk.Checkbutton(options_frame, text="Szukaj logów", variable=scan_logs, font=button_font, fg="white", bg="#2e3e46", selectcolor="#3d3d3d", activebackground="#3d3d3d")
    logs_button.grid(row=0, column=1, padx=5)

    mods_button = tk.Checkbutton(options_frame, text="Szukaj modów", variable=scan_mods, font=button_font, fg="white", bg="#2e3e46", selectcolor="#3d3d3d", activebackground="#3d3d3d")
    mods_button.grid(row=1, column=0, padx=5)

    texture_packs_button = tk.Checkbutton(options_frame, text="Szukaj paczek tekstur", variable=scan_texture_packs, font=button_font, fg="white", bg="#2e3e46", selectcolor="#3d3d3d", activebackground="#3d3d3d")
    texture_packs_button.grid(row=1, column=1, padx=5)

    download_cheats_button = tk.Checkbutton(options_frame, text="Szukaj pobranych cheatów", variable=scan_download_cheats, font=button_font, fg="white", bg="#2e3e46", selectcolor="#3d3d3d", activebackground="#3d3d3d")
    download_cheats_button.grid(row=2, column=0, padx=5, columnspan=2)

    # Przycisk rozpoczęcia skanowania
    scan_button = tk.Button(window, text="Rozpocznij skanowanie", command=start_scan_thread, font=("Arial", 14, "bold"), fg="white", bg="#4CAF50", relief="raised", height=2, width=20)
    scan_button.pack(pady=20)

    # Progresbar
    progress = ttk.Progressbar(window, length=700, mode="determinate", maximum=100)
    progress.pack(pady=15)

    # Obszar tekstowy
    log_text = tk.Text(window, height=15, width=85, font=font_style, bg="#1e1e1e", fg="white", wrap="word", bd=5, relief="sunken")
    log_text.pack(padx=20, pady=10)
    log_text.insert(tk.END, "Witaj! Kliknij 'Rozpocznij skanowanie', aby rozpocząć.\n")

    # Uruchom GUI
    window.mainloop()

# Funkcja uruchamiająca skanowanie w osobnym wątku
def start_scan_thread():
    threading.Thread(target=start_scan, daemon=True).start()

# Uruchamiamy GUI
create_gui()
