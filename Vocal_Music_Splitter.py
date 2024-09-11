import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from spleeter.separator import Separator
import os
import threading

#python -m PyInstaller --onefile --noconsole Vocal_Music_Splitter.py

class AudioSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Ses Ayrıştırıcı")
        self.root.geometry("600x250")  # Pencere boyutu
        self.root.configure(bg='#404040')

        # Butonlar ve yükleme çubuğu
        self.select_file_button = tk.Button(root, text="Ses Dosyası Seç", command=self.select_file)
        self.select_file_button.pack(pady=10)

        self.file_path_label = tk.Label(root, text="Dosya Yolu: -")
        self.file_path_label.pack(pady=5)

        self.start_button = tk.Button(root, text="Başla", command=self.start_splitting, state=tk.DISABLED)
        self.start_button.pack(pady=10)

        self.status_label = tk.Label(root, text="Durum: Hazır", bg="#404040", fg="white")
        self.status_label.pack(pady=10)

        self.progress_bar = tk.Label(root, text="", relief=tk.SUNKEN, width=40, height=2, bg="#404040", fg="white")
        self.progress_bar.pack(pady=5)

        self.file_path = None
        self.processing_thread = None

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if self.file_path:
            self.file_path_label.config(text=f"Dosya Yolu: {self.file_path}")
            self.start_button.config(state=tk.NORMAL)
            self.status_label.config(text="Durum: Hazır")

    def start_splitting(self):
        if not self.file_path:
            messagebox.showwarning("Uyarı", "Önce bir dosya seçmelisiniz.")
            return

        output_dir = filedialog.askdirectory(title="Çıktı Klasörü Seçin")  # Kullanıcıdan çıktı klasörünü seçmesini isteyin
        if not output_dir:
            messagebox.showwarning("Uyarı", "Çıktı klasörü seçilmedi.")
            return

        self.status_label.config(text="Durum: İşleniyor")
        self.update_progress_bar(0)

        # İşlemi ayrı bir thread'de çalıştır
        self.processing_thread = threading.Thread(target=self.process_audio, args=(output_dir,))
        self.processing_thread.start()

    def process_audio(self, output_dir):
        try:
            # Ses dosyasını ayır
            separator = Separator('spleeter:2stems')
            separator.separate_to_file(self.file_path, output_dir)

            # İşlem tamamlandığında
            self.status_label.config(text="Durum: Bitti")
            self.update_progress_bar(100)
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {e}")
            self.status_label.config(text="Durum: Hazır")
        finally:
            self.start_button.config(state=tk.NORMAL)

    def update_progress_bar(self, progress):
        self.progress_bar.config(text=f"{progress}% Tamamlandı")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioSplitterApp(root)
    root.mainloop()
