import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from spleeter.separator import Separator
import os
import threading
from moviepy.editor import VideoFileClip  # MP4'ü MP3'e dönüştürmek için gerekli

#python -m PyInstaller --onefile --noconsole Vocal_Music_Splitter.py

class AudioSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Ses Ayrıştırıcı ve Dönüştürücü")
        self.root.geometry("600x350")  # Pencere boyutu genişletildi
        self.root.configure(bg='#404040')

        # Butonlar ve yükleme çubuğu
        self.select_file_button = tk.Button(root, text="Ses Dosyası Seç (MP3)", command=self.select_file, bg="#28a745", fg="white")
        self.select_file_button.pack(pady=10)

        self.convert_button = tk.Button(root, text="MP4'ü MP3'e Dönüştür", command=self.convert_mp4, bg="#6c757d", fg="white")
        self.convert_button.pack(pady=10)

        self.file_path_label = tk.Label(root, text="Dosya Yolu: -", bg='#404040', fg='white')
        self.file_path_label.pack(pady=5)

        self.start_button = tk.Button(root, text="Başla (MP3 Ayrıştır)", command=self.start_splitting, state=tk.DISABLED, bg="#007bff", fg="white")
        self.start_button.pack(pady=10)

        self.status_label = tk.Label(root, text="Durum: Hazır", bg="#404040", fg="white")
        self.status_label.pack(pady=10)

        # Kaydedilecek dosya yolu etiketini ekliyoruz
        self.save_path_label = tk.Label(root, text="Kaydedilecek Yer: -", bg='#404040', fg='white')
        self.save_path_label.pack(pady=5)

        # Yükleme çubuğu çerçevesi
        self.progress_frame = tk.Frame(root, width=400, height=25, bg="#404040")
        self.progress_frame.pack(pady=5)

        # Yükleme çubuğu
        self.progress_bar = tk.Canvas(self.progress_frame, width=400, height=25, bg="white")
        self.progress_bar.pack()

        self.file_path = None
        self.processing_thread = None

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if self.file_path:
            self.file_path_label.config(text=f"Dosya Yolu: {self.file_path}")
            self.start_button.config(state=tk.NORMAL)
            self.status_label.config(text="Durum: Hazır")

    def convert_mp4(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP4 Files", "*.mp4")])
        if not file_path:
            messagebox.showwarning("Uyarı", "Bir MP4 dosyası seçmelisiniz.")
            return

        output_dir = filedialog.askdirectory(title="Çıktı Klasörü Seçin")
        if not output_dir:
            messagebox.showwarning("Uyarı", "Çıktı klasörü seçilmedi.")
            return

        self.status_label.config(text="Durum: MP4'ten MP3'e Dönüştürülüyor")
        self.save_path_label.config(text=f"Kaydedilecek Yer: {output_dir}")
        self.update_progress_bar(0)

        # Dönüştürme işlemi için thread başlat
        self.processing_thread = threading.Thread(target=self.process_mp4_to_mp3, args=(file_path, output_dir,))
        self.processing_thread.start()

    def process_mp4_to_mp3(self, file_path, output_dir):
        try:
            mp3_output_path = os.path.join(output_dir, os.path.basename(file_path).replace(".mp4", ".mp3"))
            video_clip = VideoFileClip(file_path)
            video_clip.audio.write_audiofile(mp3_output_path)

            self.status_label.config(text="Durum: Dönüştürme Tamamlandı")
            self.update_progress_bar(100)
        except Exception as e:
            messagebox.showerror("Hata", f"MP4'ten MP3'e dönüştürmede hata oluştu: {e}")
            self.status_label.config(text="Durum: Hazır")
        finally:
            self.start_button.config(state=tk.NORMAL)

    def start_splitting(self):
        if not self.file_path:
            messagebox.showwarning("Uyarı", "Önce bir MP3 dosyası seçmelisiniz.")
            return

        output_dir = filedialog.askdirectory(title="Çıktı Klasörü Seçin")
        if not output_dir:
            messagebox.showwarning("Uyarı", "Çıktı klasörü seçilmedi.")
            return

        self.status_label.config(text="Durum: İşleniyor")
        self.save_path_label.config(text=f"Kaydedilecek Yer: {output_dir}")  # Kaydedilecek dosya yolunu göster
        self.update_progress_bar(0)

        # İşlemi ayrı bir thread'de çalıştır
        self.processing_thread = threading.Thread(target=self.process_audio, args=(output_dir,))
        self.processing_thread.start()

    def process_audio(self, output_dir):
        try:
            separator = Separator('spleeter:2stems')
            separator.separate_to_file(self.file_path, output_dir)
            self.status_label.config(text="Durum: Bitti")
            self.update_progress_bar(100)
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {e}")
            self.status_label.config(text="Durum: Hazır")
        finally:
            self.start_button.config(state=tk.NORMAL)

    def update_progress_bar(self, progress):
        self.progress_bar.delete("all")
        bar_length = 400 * (progress / 100)
        self.progress_bar.create_rectangle(0, 0, bar_length, 25, fill="green")
        self.progress_bar.create_text(200, 12, text=f"%{progress}", fill="black")  # Yüzdelik gösterimi
        self.progress_bar.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioSplitterApp(root)
    root.mainloop()
