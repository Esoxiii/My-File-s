import os
import tkinter as tk
from tkinter import messagebox, Scrollbar, Text, filedialog
import time
import threading
import re
import shutil

# Lista podejrzanych plików cheatów
cheat_files = [
    "Mango.jar",
    "MangoClient.jar",
    "Xray.zip",
    "Meteor.jar",
    "MeteorClient.jar",
    "XrayMod.zip",
    "cheatmod.jar",
    "hackclient.exe",
    "xraymod.jar",
    "hackedclient.jar"
]

# Funkcja do konwersji czasu (np. '1d' na 86400 sekund)
def convert_time_to_seconds(time_str):
    pattern = re.compile(r'(\d+)([dhm])')
    match = pattern.fullmatch(time_str.lower())
    if not match:
        raise ValueError("Niepoprawny format czasu. Użyj 'd' dla dni, 'h' dla godzin, 'm' dla minut.")
    number, unit = match.groups()
    number = int(number)
    if unit == 'd':
        return number * 86400  # dni na sekundy
    elif unit == 'h':
        return number * 3600  # godziny na sekundy
    elif unit == 'm':
        return number * 60  # minuty na sekundy

# Funkcja do sprawdzania cheatów w wybranym folderze
def check_cheats(minecraft_folder, root, last_used_time_limit, save_to_file, file_types):
    result_text.delete(1.0, tk.END)  # Czyszczenie poprzednich wyników
    status_label.config(text="Sprawdzanie plików...")  # Ustawiamy status
    found_cheats = []
    
    try:
        if not os.path.exists(minecraft_folder):
            messagebox.showerror("Błąd", f"Ścieżka do folderu Minecraft nie istnieje: {minecraft_folder}")
            return

        total_files = 0
        checked_files = 0

        # Przechodzimy po wszystkich plikach w folderze Minecraft
        for root_dir, dirs, files in os.walk(minecraft_folder):
            total_files = len(files)
            for file in files:
                file_path = os.path.join(root_dir, file)

                # Sprawdzamy, czy plik pasuje do wybranych typów
                if file_types and not any(file.lower().endswith(ext) for ext in file_types):
                    continue

                # Ignorujemy pliki starsze niż ustawiony limit czasu
                if time.time() - os.path.getmtime(file_path) > last_used_time_limit:
                    continue

                # Sprawdzamy, czy nazwa pliku jest na liście cheatów (ignorując wielkość liter)
                if any(cheat.lower() == file.lower() for cheat in cheat_files):
                    last_used_time = time.ctime(os.path.getmtime(file_path))  # Czas ostatniego użycia
                    found_cheats.append(f"Potencjalny cheat wykryty: {file_path} (Ostatnie użycie: {last_used_time})")

                checked_files += 1
                # Zaktualizowanie statusu postępu
                if total_files > 0:
                    progress = (checked_files / total_files) * 100
                    progress_label.config(text=f"Procent zakończenia: {progress:.2f}%")
                    root.update_idletasks()  # Odświeżenie GUI, aby pokazać postęp

        # Po zakończeniu skanowania
        if not found_cheats:
            result_text.insert(tk.END, "Brak wykrytych cheatów.\n")
        else:
            for cheat in found_cheats:
                result_text.insert(tk.END, cheat + "\n")
            
            # Zapisanie wykrytych cheatów do pliku, jeśli użytkownik zaznaczył opcję
            if save_to_file:
                with open("cheats_found.txt", "w") as file:
                    for cheat in found_cheats:
                        file.write(cheat + "\n")

        # Wyświetlenie 100% postępu po zakończeniu
        progress_label.config(text="Procent zakończenia: 100%")
        status_label.config(text="Sprawdzanie zakończone.")  # Status po zakończeniu

    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")
        status_label.config(text="Błąd podczas sprawdzania.")  # Status przy błędzie

# Funkcja do otwierania okna dialogowego i wybierania folderu
def select_folder(root, time_limit, save_to_file, file_types):
    folder_path = filedialog.askdirectory(title="Wybierz folder Minecraft")
    if folder_path:
        # Uruchamiamy skanowanie w osobnym wątku
        threading.Thread(target=check_cheats, args=(folder_path, root, time_limit, save_to_file, file_types), daemon=True).start()

# Funkcja do tworzenia GUI
def create_gui():
    root = tk.Tk()
    root.title("Wykrywanie Cheatów w Minecraft")
    root.config(bg="#2e3b4e")

    # Etykieta dla wprowadzenia czasu
    time_label = tk.Label(root, text="Czas ostatniego użycia (np. '1d' dla 1 dnia, '1h' dla 1 godziny, '30m' dla 30 minut):",
                          font=("Arial", 12), fg="white", bg="#2e3b4e")
    time_label.grid(row=0, column=0, padx=20, pady=5, sticky="w")

    # Pole do wprowadzenia czasu
    global time_input
    time_input = tk.Entry(root, font=("Arial", 12), width=20)
    time_input.grid(row=0, column=1, padx=20, pady=5)

    # Zmienna kontrolna dla checkboxa
    global save_to_file_var
    save_to_file_var = tk.BooleanVar(value=True)

    # Checkbox do zapisywania wyników
    global save_checkbox
    save_checkbox = tk.Checkbutton(root, text="Zapisz wyniki do pliku txt", variable=save_to_file_var, font=("Arial", 12), fg="white", bg="#2e3b4e", selectcolor="#4C8BF5")
    save_checkbox.grid(row=1, columnspan=2, padx=20, pady=10)

    # Wybór typu plików do skanowania
    file_type_label = tk.Label(root, text="Wybierz typy plików (opcjonalnie):", font=("Arial", 12), fg="white", bg="#2e3b4e")
    file_type_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")

    file_types_var = tk.StringVar(value="jar,exe,zip")  # Domyślnie sprawdzamy .jar, .exe, .zip
    file_types_entry = tk.Entry(root, font=("Arial", 12), textvariable=file_types_var, width=20)
    file_types_entry.grid(row=2, column=1, padx=20, pady=5)

    # Przyciski
    start_button = tk.Button(root, text="Wybierz folder i sprawdź Cheaty", font=("Arial", 12), fg="white", bg="#4C8BF5", command=lambda: start_scan(root, file_types_var))
    start_button.grid(row=3, columnspan=2, padx=20, pady=20)

    # Status Label
    global status_label
    status_label = tk.Label(root, text="Witaj, kliknij 'Wybierz folder i sprawdź Cheaty', aby zacząć.", font=("Arial", 12), fg="blue", bg="#2e3b4e")
    status_label.grid(row=4, columnspan=2, padx=20, pady=5)

    # Procent zakończenia
    global progress_label
    progress_label = tk.Label(root, text="Procent zakończenia: 0%", font=("Arial", 12), fg="green", bg="#2e3b4e")
    progress_label.grid(row=5, columnspan=2, padx=20, pady=5)

    # Scrollbar i Text do wyświetlania wyników
    scroll_bar = Scrollbar(root)
    scroll_bar.grid(row=6, column=2, sticky="ns", pady=20)

    global result_text
    result_text = Text(root, height=15, width=80, wrap=tk.WORD, yscrollcommand=scroll_bar.set, font=("Arial", 12))
    result_text.grid(row=6, columnspan=2, padx=20, pady=20)
    scroll_bar.config(command=result_text.yview)

    root.geometry("700x550")
    root.mainloop()

def start_scan(root, file_types_var):
    # Pobieramy czas z pola wejściowego
    time_limit_str = time_input.get()
    try:
        # Konwertujemy czas na sekundy
        time_limit = convert_time_to_seconds(time_limit_str)
        # Pobieramy stan checkboxa
        save_to_file = save_to_file_var.get()
        # Pobieramy rozszerzenia plików z pola wejściowego
        file_types = file_types_var.get().split(",")
        # Uruchamiamy skanowanie
        select_folder(root, time_limit, save_to_file, file_types)
    except ValueError as e:
        messagebox.showerror("Błąd", f"Niepoprawny format czasu: {e}")

# Uruchamiamy GUI
create_gui()
