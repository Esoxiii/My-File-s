import cv2
import tkinter as tk
from tkinter import messagebox
import winsound
import threading
from PIL import Image, ImageTk

# Funkcja do uruchomienia alarmu
def uruchom_alarm():
    winsound.Beep(1000, 500)  # Dźwięk alarmu - częstotliwość 1000 Hz przez 500 ms

# Funkcja detekcji twarzy i wykrywania ruchu
def detekcja(canvas, root, alarm_uruchomiony):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    cap = cv2.VideoCapture(0)  # Używamy kamery internetowej (domyślnej)
    
    if not cap.isOpened():
        messagebox.showerror("Błąd", "Nie udało się otworzyć kamery!")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Wykrywanie twarzy
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # Jeśli wykryto twarz, uruchom alarm
        if len(faces) > 0 and not alarm_uruchomiony[0]:
            threading.Thread(target=uruchom_alarm).start()  # Uruchom alarm w osobnym wątku
            alarm_uruchomiony[0] = True  # Alarm został uruchomiony
                
        elif len(faces) == 0:
            alarm_uruchomiony[0] = False  # Reset alarmu, gdy brak twarzy
            
        # Przerysuj wykryte twarze
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # Konwertowanie obrazu do formatu akceptowanego przez Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Ustawienie obrazu na Canvasie
        canvas.create_image(0, 0, anchor="nw", image=imgtk)
        canvas.imgtk = imgtk  # Zachowaj odniesienie do obrazu, aby zapobiec jego zniknięciu
        
        # Aktualizacja GUI
        root.after(10, detekcja, canvas, root, alarm_uruchomiony)  # Ponownie wywołanie detekcji po 10ms

    cap.release()  # Zwolnij zasoby kamery po zakończeniu

# Funkcja uruchamiająca detekcję w osobnym wątku
def uruchom_detekcje(canvas, root, alarm_uruchomiony):
    threading.Thread(target=detekcja, args=(canvas, root, alarm_uruchomiony), daemon=True).start()

# Funkcja aktywująca czuwanie
def aktywuj_czuwanie(canvas, root, alarm_uruchomiony):
    alarm_uruchomiony[0] = False  # Resetuj alarm przed aktywowaniem czuwania
    uruchom_detekcje(canvas, root, alarm_uruchomiony)

# Tworzymy GUI z Tkinter
root = tk.Tk()
root.title("Detekcja Twarzy i Alarm")

# Ustawienie rozmiaru okna
root.geometry("800x600")

# Tworzymy Canvas do wyświetlania obrazu
canvas = tk.Canvas(root, width=640, height=480)
canvas.pack(pady=20)

# Tworzymy przycisk do uruchomienia czuwania
czuwanie_button = tk.Button(root, text="Włącz czuwanie", command=lambda: aktywuj_czuwanie(canvas, root, [False]))
czuwanie_button.pack(pady=50)

# Przechowywanie informacji o stanie alarmu
alarm_uruchomiony = [False]  # Zmienna w liście, aby można było ją zmieniać w wątkach

# Uruchamiamy aplikację
root.mainloop()