import tkinter as tk
from tkinter import filedialog, messagebox
from spleeter.separator import Separator
import os
import threading
import time

class LoadingScreen:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Yükleniyor")
        self.top.geometry("300x100")
        self.top.configure(bg='#404040')
        self.label = tk.Label(self.top, text="Yükleniyor, lütfen bekleyin...", bg='#404040', fg='white', font=("Arial", 12))
        self.label.pack(pady=20)
        self.progress_bar = tk.Canvas(self.top, width=250, height=20, bg="white")
        self.progress_bar.pack(pady=10)
        self.bar = self.progress_bar.create_rectangle(0, 0, 0, 20, fill="green")
        self.update()

    def update(self):
        current_width = self.progress_bar.coords(self.bar)[2]
        if current_width < 250:
            self.progress_bar.move(self.bar, 5, 0)
            self.top.after(50, self.update)
        else:
            self.top.destroy()

class AudioSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Ses Ayrıştırıcı ve Dönüştürücü")
        self.root.geometry("800x400")
        self.root.configure(bg='#404040')

        # Uygulama başlatıldığında yükleme ekranı göstermek için
        self.loading_screen = LoadingScreen(self.root)
        self.root.after(2000, self.initialize_ui)  # 2 saniye sonra UI'yi başlat

    def initialize_ui(self):
        self.loading_screen.top.destroy()  # Yükleme ekranını kapat

        # Model seçme butonu
        self.model_list_label = tk.Label(self.root, text="Model Seçin:", bg='#404040', fg='white')
        self.model_list_label.pack(pady=5)

        self.model_var = tk.StringVar(self.root)
        self.model_var.set("Model bulunamadı")  # Varsayılan değer

        # Model seçeneklerini bul ve dropdown menüsünü oluştur
        model_files = self.find_model_files()
        self.model_dropdown = tk.OptionMenu(self.root, self.model_var, *model_files, command=self.update_model)
        self.model_dropdown.pack(pady=10)

        # "Göz At" butonu
        self.browse_button = tk.Button(self.root, text="Göz At", command=self.select_model, bg="#ff9900", fg="white")
        self.browse_button.pack(pady=10)

        # Seçilen modelin adı
        self.model_name_label = tk.Label(self.root, text=f"Seçilen Model: {self.model_var.get()}", bg='#404040', fg='white')
        self.model_name_label.pack(pady=5)

        # Ses dosyası seçme butonu
        self.select_file_button = tk.Button(self.root, text="Ses Dosyası Seç (MP3/MP4)", command=self.select_file, bg="#28a745", fg="white")
        self.select_file_button.pack(pady=10)

        self.file_path_label = tk.Label(self.root, text="Dosya Yolu: -", bg='#404040', fg='white')
        self.file_path_label.pack(pady=5)

        self.start_button = tk.Button(self.root, text="Başla (MP3 Ayrıştır)", command=self.start_splitting, state=tk.DISABLED, bg="#007bff", fg="white")
        self.start_button.pack(pady=10)

        self.status_label = tk.Label(self.root, text="Durum: Hazır", bg="#404040", fg="white")
        self.status_label.pack(pady=10)

        self.progress_frame = tk.Frame(self.root, width=400, height=25, bg="#404040")
        self.progress_frame.pack(pady=5)

        self.progress_bar = tk.Canvas(self.progress_frame, width=400, height=25, bg="white")
        self.progress_bar.pack()

        self.file_path = None
        self.model_path = None
        self.processing_thread = None

        # Varsayılan model yolunu belirle
        self.default_model = "2stems-finetune.tar.gz"
        self.model_path = os.path.join(self.find_model_dir(), self.default_model)
        self.model_var.set(self.default_model)

    def find_model_files(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(script_dir, 'models')
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.tar.gz')]
        
        if model_files:
            return model_files
        return ["Model bulunamadı"]

    def find_model_dir(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')

    def update_model(self, selected_model):
        self.model_path = os.path.join(self.find_model_dir(), selected_model)
        self.model_name_label.config(text=f"Seçilen Model: {selected_model}")

    def select_model(self):
        self.model_path = filedialog.askopenfilename(filetypes=[("Tar.gz Files", "*.tar.gz")])
        if self.model_path:
            model_name = os.path.basename(self.model_path)
            self.model_var.set(model_name)
            self.update_model(model_name)

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("MP3/MP4 Files", "*.mp3 *.mp4")])
        if self.file_path:
            self.file_path_label.config(text=f"Dosya Yolu: {self.file_path}")
            self.start_button.config(state=tk.NORMAL)
            self.status_label.config(text="Durum: Hazır")

    def start_splitting(self):
        if not self.file_path:
            messagebox.showwarning("Uyarı", "Önce bir ses dosyası seçmelisiniz.")
            return

        if not self.model_var.get() or self.model_var.get() == "Model bulunamadı":
            messagebox.showwarning("Uyarı", "Önce bir model dosyası seçmelisiniz.")
            return

        output_dir = filedialog.askdirectory(title="Çıktı Klasörü Seçin")
        if not output_dir:
            messagebox.showwarning("Uyarı", "Çıktı klasörü seçilmedi.")
            return

        self.status_label.config(text="Durum: İşleniyor")
        self.update_progress_bar(0)

        # Yükleme ekranını göster
        self.loading_screen = LoadingScreen(self.root)
        self.processing_thread = threading.Thread(target=self.process_audio, args=(output_dir,))
        self.processing_thread.start()

    def process_audio(self, output_dir):
        try:
            splitted_dir = os.path.join(output_dir, "Splitted")
            os.makedirs(splitted_dir, exist_ok=True)

            # Seçilen model dosyası
            selected_model = self.model_var.get()
            model_name = selected_model.split('.')[0]  # Uzantıyı kaldır

            # Spleeter ile ayırma işlemi
            separator = Separator(f'spleeter:{model_name.split("-")[0]}')  # 2stems, 4stems veya 5stems gibi
            # Simülasyon: İşlem süresi ve ilerleme güncellemesi
            total_steps = 100
            for i in range(total_steps):
                time.sleep(0.05)  # Simülasyon için bekleme
                self.update_progress_bar((i + 1) * (100 // total_steps))
            
            separator.separate_to_file(self.file_path, splitted_dir)

            self.status_label.config(text="Durum: Bitti")
            self.update_progress_bar(100)
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {e}")
            self.status_label.config(text="Durum: Hazır")
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.loading_screen.top.destroy()  # Yükleme ekranını kapat

    def update_progress_bar(self, progress):
        self.progress_bar.delete("all")
        bar_length = 400 * (progress / 100)
        self.progress_bar.create_rectangle(0, 0, bar_length, 25, fill="green")
        self.progress_bar.create_text(200, 12, text=f"%{progress}", fill="black")
        self.progress_bar.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioSplitterApp(root)
    root.mainloop()
