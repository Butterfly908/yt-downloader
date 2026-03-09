import os
import sys
import threading
import queue
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from yt_dlp import YoutubeDL

APP_STATE_IDLE = "idle"
APP_STATE_CHECKING = "checking"
APP_STATE_DOWNLOADING = "downloading"
APP_STATE_CANCELLING = "cancelling"

MSG_FORMATS_LOADED = "formats_loaded"
MSG_FORMATS_ERROR = "formats_error"
MSG_PROGRESS = "progress"
MSG_STAGE = "stage"
MSG_FINISHED = "finished"
MSG_CANCELLED = "cancelled"
MSG_ERROR = "error"
MSG_LOG = "log"

LOG_DEBUG = "DEBUG"
LOG_INFO = "INFO"
LOG_WARNING = "WARNING"
LOG_ERROR = "ERROR"

save_folder = ""
formats_map = {}
formats_map_simple = {}
formats_map_advanced = {}

is_checking = False
quality_mode = None
app_state = APP_STATE_IDLE

ui_queue = queue.Queue()
download_thread = None
check_thread = None
cancel_event = threading.Event()
close_requested = False

app_log_lines = []


class DownloadCancelled(Exception):
    pass


class YTDLPLogger:
    def debug(self, msg):
        if msg:
            post_ui_message(MSG_LOG, level=LOG_DEBUG, text=str(msg))

    def info(self, msg):
        if msg:
            post_ui_message(MSG_LOG, level=LOG_INFO, text=str(msg))

    def warning(self, msg):
        if msg:
            post_ui_message(MSG_LOG, level=LOG_WARNING, text=str(msg))

    def error(self, msg):
        if msg:
            post_ui_message(MSG_LOG, level=LOG_ERROR, text=str(msg))


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def extract_height(label):
    try:
        return int(label.split("p")[0])
    except Exception:
        return 0


def now_str():
    return datetime.now().strftime("%H:%M:%S")


def post_ui_message(msg_type, **payload):
    ui_queue.put({"type": msg_type, **payload})


def append_log(level, text):
    line = f"[{now_str()}] [{level}] {text}"
    app_log_lines.append(line)

    max_lines = 2000
    if len(app_log_lines) > max_lines:
        del app_log_lines[:-max_lines]


def log_message(level, text):
    post_ui_message(MSG_LOG, level=level, text=text)


def save_log_to_file():
    if not app_log_lines:
        messagebox.showinfo("Лог", "Лог пуст")
        return

    path = filedialog.asksaveasfilename(
        title="Сохранить лог",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not path:
        return

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(app_log_lines))
        messagebox.showinfo("Успех", "Лог сохранён")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


def cleanup_temp_by_filename(filename):
    if not filename:
        return

    folder = os.path.dirname(filename)
    base = os.path.basename(filename)

    candidates = [
        filename,
        filename + ".part",
        filename + ".ytdl",
        filename + ".temp",
    ]

    stem, _ = os.path.splitext(filename)
    candidates.extend([
        stem + ".part",
        stem + ".ytdl",
        stem + ".temp",
    ])

    for path in candidates:
        try:
            if os.path.isfile(path):
                os.remove(path)
        except Exception:
            pass

    if folder and os.path.isdir(folder):
        try:
            name_only = os.path.splitext(base)[0]
            for item in os.listdir(folder):
                full = os.path.join(folder, item)
                if not os.path.isfile(full):
                    continue
                if name_only in item and (
                    item.endswith(".part")
                    or item.endswith(".ytdl")
                    or item.endswith(".temp")
                ):
                    try:
                        os.remove(full)
                    except Exception:
                        pass
        except Exception:
            pass


def reset_progressbar():
    try:
        progress_bar.stop()
    except Exception:
        pass

    progress_bar.config(mode="determinate", maximum=100)
    progress_bar["value"] = 0

    progress_style.configure(
        "Custom.Horizontal.TProgressbar",
        troughcolor="#dfe3ea",
        background="#3b82f6",
        bordercolor="#dfe3ea",
        lightcolor="#3b82f6",
        darkcolor="#3b82f6"
    )


def set_progress_indeterminate(color="#3b82f6"):
    try:
        progress_bar.stop()
    except Exception:
        pass

    progress_style.configure(
        "Custom.Horizontal.TProgressbar",
        troughcolor="#dfe3ea",
        background=color,
        bordercolor="#dfe3ea",
        lightcolor=color,
        darkcolor=color
    )
    progress_bar.config(mode="indeterminate")
    progress_bar.start(12)


def set_progress_determinate(value=0, color="#3b82f6"):
    try:
        progress_bar.stop()
    except Exception:
        pass

    progress_style.configure(
        "Custom.Horizontal.TProgressbar",
        troughcolor="#dfe3ea",
        background=color,
        bordercolor="#dfe3ea",
        lightcolor=color,
        darkcolor=color
    )
    progress_bar.config(mode="determinate", maximum=100)
    progress_bar["value"] = max(0, min(100, value))


def set_state(new_state):
    global app_state
    app_state = new_state

    if new_state == APP_STATE_IDLE:
        url_entry.config(state="normal")
        folder_button.config(state="normal", bg="#e5e7eb", activebackground="#d1d5db")
        open_folder_button.config(state="normal", bg="#e5e7eb", activebackground="#d1d5db")
        check_button.config(state="normal", bg="#e5e7eb", activebackground="#d1d5db")
        simple_radio.config(state="normal")
        advanced_radio.config(state="normal")

        if formats_map:
            quality_combo.config(state="readonly")
            download_button.config(state="normal", bg="#2563eb", activebackground="#1d4ed8")
        else:
            quality_combo.config(state="disabled")
            download_button.config(state="disabled", bg="#93c5fd", activebackground="#93c5fd")

        cancel_button.config(state="disabled", bg="#f3b0b0", activebackground="#f3b0b0")

    elif new_state == APP_STATE_CHECKING:
        url_entry.config(state="disabled")
        folder_button.config(state="disabled")
        open_folder_button.config(state="disabled")
        check_button.config(state="disabled")
        quality_combo.config(state="disabled")
        download_button.config(state="disabled")
        cancel_button.config(state="disabled")
        simple_radio.config(state="disabled")
        advanced_radio.config(state="disabled")

    elif new_state == APP_STATE_DOWNLOADING:
        url_entry.config(state="disabled")
        folder_button.config(state="disabled")
        open_folder_button.config(state="disabled")
        check_button.config(state="disabled")
        quality_combo.config(state="disabled")
        download_button.config(state="disabled")
        simple_radio.config(state="disabled")
        advanced_radio.config(state="disabled")
        cancel_button.config(state="normal", bg="#dc2626", activebackground="#b91c1c", fg="white")

    elif new_state == APP_STATE_CANCELLING:
        url_entry.config(state="disabled")
        folder_button.config(state="disabled")
        open_folder_button.config(state="disabled")
        check_button.config(state="disabled")
        quality_combo.config(state="disabled")
        download_button.config(state="disabled")
        simple_radio.config(state="disabled")
        advanced_radio.config(state="disabled")
        cancel_button.config(state="disabled", bg="#f3b0b0", activebackground="#f3b0b0")


def refresh_quality_list():
    global formats_map

    mode = quality_mode.get()

    if mode == "simple":
        formats_map = formats_map_simple.copy()
    else:
        formats_map = formats_map_advanced.copy()

    values = list(formats_map.keys())
    quality_combo["values"] = values

    if values:
        current = quality_combo.get()
        if current in values:
            quality_combo.set(current)
        else:
            quality_combo.set(values[0])
    else:
        quality_combo.set("")

    if app_state == APP_STATE_IDLE:
        set_state(APP_STATE_IDLE)


def choose_folder():
    global save_folder
    folder = filedialog.askdirectory(title="Выберите папку")
    if folder:
        save_folder = folder
        folder_label.config(text=save_folder)
        log_message(LOG_INFO, f"Выбрана папка: {save_folder}")


def open_folder():
    if not save_folder:
        messagebox.showwarning("Внимание", "Сначала выберите папку")
        return
    if os.path.exists(save_folder):
        os.startfile(save_folder)
        log_message(LOG_INFO, f"Открыта папка: {save_folder}")
    else:
        messagebox.showerror("Ошибка", "Папка не найдена")


def on_quality_mode_change():
    if formats_map_simple or formats_map_advanced:
        refresh_quality_list()
        log_message(LOG_INFO, f"Режим качества переключен: {quality_mode.get()}")


def load_formats_worker(url):
    log_message(LOG_INFO, "Старт проверки качеств")
    log_message(LOG_INFO, "-" * 70)
    log_message(LOG_INFO, f"Запрошена проверка качеств: {url}")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "logger": YTDLPLogger(),
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get("formats", [])
        title = info.get("title", "Без названия")
        log_message(LOG_INFO, f"Получена информация о видео: {title}")

        advanced_map = {}
        simple_candidates = {}
        audio_added = False

        for f in formats:
            format_id = f.get("format_id")
            ext = f.get("ext", "unknown")
            height = f.get("height")
            vcodec = f.get("vcodec")
            filesize = f.get("filesize") or f.get("filesize_approx") or 0
            tbr = f.get("tbr") or 0

            if not format_id:
                continue

            if vcodec != "none" and height:
                size_mb = f" | {round(filesize / 1024 / 1024, 1)} MB" if filesize else ""
                advanced_label = f"{height}p | {ext} | id={format_id}{size_mb}"
                advanced_map[advanced_label] = format_id

                score = (height, tbr, filesize)
                simple_label = f"{height}p"

                if height not in simple_candidates or score > simple_candidates[height]["score"]:
                    simple_candidates[height] = {
                        "label": simple_label,
                        "format_id": format_id,
                        "score": score
                    }

            elif vcodec == "none" and not audio_added:
                advanced_map["Только аудио (mp3)"] = "bestaudio"
                audio_added = True

        simple_map = {}
        for height in sorted(simple_candidates.keys(), reverse=True):
            item = simple_candidates[height]
            simple_map[item["label"]] = item["format_id"]

        if audio_added:
            simple_map["Только аудио (mp3)"] = "bestaudio"

        advanced_map = dict(
            sorted(
                advanced_map.items(),
                key=lambda item: (
                    9999 if item[0] == "Только аудио (mp3)" else -extract_height(item[0])
                )
            )
        )

        log_message(LOG_INFO, f"Качеств найдено: обычных={len(simple_map)}, продвинутых={len(advanced_map)}")
        post_ui_message(MSG_FORMATS_LOADED, simple_map=simple_map, advanced_map=advanced_map)

    except Exception as e:
        log_message(LOG_ERROR, f"Ошибка получения качеств: {e}")
        post_ui_message(MSG_FORMATS_ERROR, error_text=str(e))


def check_formats():
    global is_checking, check_thread

    url = url_entry.get().strip()
    if url == "":
        messagebox.showerror("Ошибка", "Введите ссылку на видео")
        return

    if app_state != APP_STATE_IDLE:
        return

    is_checking = True
    quality_combo.set("")
    quality_combo["values"] = []
    reset_progressbar()
    status_label.config(text="Получение доступных качеств...")
    set_state(APP_STATE_CHECKING)

    check_thread = threading.Thread(target=load_formats_worker, args=(url,), daemon=True)
    check_thread.start()


def download_worker(url, save_path, selected_format):
    downloaded_filename = None
    prepared_name = None

    def hook(d):
        nonlocal downloaded_filename

        if cancel_event.is_set():
            raise DownloadCancelled("Загрузка отменена пользователем")

        filename = d.get("filename")
        if filename:
            downloaded_filename = filename

        status = d.get("status")

        if status == "downloading":
            percent_value = None
            text = "Скачивание..."

            downloaded_bytes = d.get("downloaded_bytes")
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")

            if downloaded_bytes is not None and total_bytes:
                try:
                    percent_value = (downloaded_bytes / total_bytes) * 100
                except Exception:
                    percent_value = None

            percent_str = d.get("_percent_str", "").strip()
            speed = d.get("_speed_str", "...")
            eta = d.get("_eta_str", "...")

            if percent_str:
                text = f"Скачивание... {percent_str} | Скорость: {speed} | Осталось: {eta}"

            post_ui_message(MSG_PROGRESS, text=text, percent=percent_value)

        elif status == "finished":
            if filename:
                downloaded_filename = filename
            log_message(LOG_INFO, f"Этап скачивания завершён: {filename if filename else 'без имени'}")
            post_ui_message(MSG_STAGE, text="Обработка файла...")

    logger = YTDLPLogger()

    if selected_format == "bestaudio":
        outtmpl = os.path.join(save_path, "%(title)s [audio].%(ext)s")
        ydl_opts = {
            "outtmpl": outtmpl,
            "progress_hooks": [hook],
            "noplaylist": True,
            "format": "bestaudio/best",
            "logger": logger,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
        }
    else:
        outtmpl = os.path.join(save_path, "%(title)s [%(height)sp].%(ext)s")
        ydl_opts = {
            "outtmpl": outtmpl,
            "progress_hooks": [hook],
            "noplaylist": True,
            "merge_output_format": "mp4",
            "format": f"{selected_format}+bestaudio/best",
            "logger": logger,
        }

    try:
        log_message(LOG_INFO, "Нажата кнопка Скачать")
        log_message(LOG_INFO, "-" * 70)
        log_message(LOG_INFO, f"Старт загрузки: {url}")
        log_message(LOG_INFO, f"Папка сохранения: {save_path}")
        log_message(LOG_INFO, f"Выбранный формат: {selected_format}")
        post_ui_message(MSG_STAGE, text="Подготовка...")

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            prepared_name = ydl.prepare_filename(info)
            log_message(LOG_INFO, f"Подготовлен путь: {prepared_name}")

            if cancel_event.is_set():
                raise DownloadCancelled("Загрузка отменена пользователем")

            ydl.download([url])

        if cancel_event.is_set():
            cleanup_temp_by_filename(downloaded_filename)
            cleanup_temp_by_filename(prepared_name)
            log_message(LOG_WARNING, "Загрузка отменена после завершения worker")
            post_ui_message(MSG_CANCELLED)
            return

        log_message(LOG_INFO, "Загрузка успешно завершена")
        post_ui_message(MSG_FINISHED)

    except DownloadCancelled:
        cleanup_temp_by_filename(downloaded_filename)
        cleanup_temp_by_filename(prepared_name)
        log_message(LOG_WARNING, "Пользователь отменил загрузку")
        post_ui_message(MSG_CANCELLED)

    except Exception as e:
        cleanup_temp_by_filename(downloaded_filename)
        cleanup_temp_by_filename(prepared_name)
        log_message(LOG_ERROR, f"Ошибка загрузки: {e}")
        post_ui_message(MSG_ERROR, error_text=str(e))


def start_download():
    global download_thread

    url = url_entry.get().strip()
    selected_label = quality_combo.get()

    if url == "":
        messagebox.showerror("Ошибка", "Введите ссылку на видео")
        return

    if save_folder == "":
        messagebox.showerror("Ошибка", "Выберите папку для сохранения")
        return

    if selected_label == "":
        messagebox.showerror("Ошибка", "Сначала нажмите 'Проверить качества'")
        return

    if selected_label not in formats_map:
        messagebox.showerror("Ошибка", "Выберите доступное качество")
        return

    if app_state != APP_STATE_IDLE:
        return

    cancel_event.clear()
    reset_progressbar()
    set_progress_indeterminate("#3b82f6")
    status_label.config(text="Подготовка...")
    set_state(APP_STATE_DOWNLOADING)

    selected_format = formats_map[selected_label]
    download_thread = threading.Thread(
        target=download_worker,
        args=(url, save_folder, selected_format),
        daemon=True
    )
    download_thread.start()


def cancel_download():
    if app_state not in (APP_STATE_DOWNLOADING, APP_STATE_CANCELLING):
        return

    cancel_event.set()
    log_message(LOG_WARNING, "Нажата кнопка Отмена")
    status_label.config(text="Остановка загрузки...")
    set_progress_indeterminate("#ef4444")
    set_state(APP_STATE_CANCELLING)


def handle_formats_loaded(message):
    global formats_map_simple, formats_map_advanced, is_checking

    is_checking = False
    formats_map_simple = message["simple_map"]
    formats_map_advanced = message["advanced_map"]

    refresh_quality_list()
    status_label.config(text="Качества загружены")
    reset_progressbar()
    set_state(APP_STATE_IDLE)


def handle_formats_error(message):
    global is_checking

    is_checking = False
    quality_combo.set("")
    quality_combo["values"] = []
    reset_progressbar()
    status_label.config(text="Ошибка получения качеств")
    set_state(APP_STATE_IDLE)
    download_button.config(state="disabled", bg="#93c5fd", activebackground="#93c5fd")
    messagebox.showerror("Ошибка", message.get("error_text", "Неизвестная ошибка"))


def handle_progress(message):
    text = message.get("text", "Скачивание...")
    percent = message.get("percent")

    status_label.config(text=text)

    if percent is not None:
        set_progress_determinate(int(percent), "#3b82f6")
    else:
        set_progress_indeterminate("#3b82f6")


def handle_stage(message):
    text = message.get("text", "Обработка файла...")
    status_label.config(text=text)
    set_progress_indeterminate("#3b82f6")


def handle_finished():
    set_progress_determinate(100, "#22c55e")
    status_label.config(text="Готово!")
    set_state(APP_STATE_IDLE)
    messagebox.showinfo("Успех", "Скачивание завершено")


def handle_cancelled():
    set_progress_determinate(0, "#ef4444")
    status_label.config(text="Загрузка отменена")
    set_state(APP_STATE_IDLE)
    messagebox.showinfo("Отмена", "Загрузка остановлена")


def handle_error(message):
    set_progress_determinate(0, "#ef4444")
    status_label.config(text="Ошибка")
    set_state(APP_STATE_IDLE)
    messagebox.showerror("Ошибка", message.get("error_text", "Неизвестная ошибка"))


def handle_log(message):
    level = message.get("level", LOG_INFO)
    text = message.get("text", "")
    append_log(level, text)


def process_ui_queue():
    if close_requested:
        return

    try:
        while True:
            message = ui_queue.get_nowait()
            msg_type = message.get("type")

            if msg_type == MSG_FORMATS_LOADED:
                handle_formats_loaded(message)
            elif msg_type == MSG_FORMATS_ERROR:
                handle_formats_error(message)
            elif msg_type == MSG_PROGRESS:
                handle_progress(message)
            elif msg_type == MSG_STAGE:
                handle_stage(message)
            elif msg_type == MSG_FINISHED:
                handle_finished()
            elif msg_type == MSG_CANCELLED:
                handle_cancelled()
            elif msg_type == MSG_ERROR:
                handle_error(message)
            elif msg_type == MSG_LOG:
                handle_log(message)

    except queue.Empty:
        pass

    root.after(100, process_ui_queue)


def on_close():
    global close_requested
    close_requested = True
    cancel_event.set()
    root.destroy()


def build_ui():
    global root
    global url_entry, quality_combo, folder_label, progress_bar, status_label
    global check_button, download_button, cancel_button, folder_button, open_folder_button
    global progress_style, quality_mode, simple_radio, advanced_radio

    root = tk.Tk()
    root.title("YT downloader")
    root.geometry("860x860")
    root.minsize(860, 860)
    root.configure(bg="#eef2f7")
    root.protocol("WM_DELETE_WINDOW", on_close)

    try:
        icon_path = resource_path("app.ico")
        root.iconbitmap(default=icon_path)
    except Exception:
        pass

    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")

    progress_style = ttk.Style()
    progress_style.configure(
        "Custom.Horizontal.TProgressbar",
        troughcolor="#dfe3ea",
        background="#3b82f6",
        bordercolor="#dfe3ea",
        lightcolor="#3b82f6",
        darkcolor="#3b82f6",
        thickness=16
    )

    card = tk.Frame(root, bg="#ffffff", bd=0, highlightthickness=0)
    card.place(relx=0.5, rely=0.5, anchor="center", width=650)

    title_label = tk.Label(
        card,
        text="YT Downloader",
        font=("Segoe UI", 28, "bold"),
        bg="#ffffff",
        fg="#111827"
    )
    title_label.pack(pady=(18, 28))

    url_label = tk.Label(
        card,
        text="Ссылка на видео",
        font=("Segoe UI", 11, "bold"),
        bg="#ffffff",
        fg="#374151",
        anchor="w"
    )
    url_label.pack(fill="x", padx=34)

    url_entry = ttk.Entry(card, font=("Segoe UI", 11))
    url_entry.pack(fill="x", padx=34, pady=(8, 18), ipady=8)

    check_button = tk.Button(
        card,
        text="Проверить качества",
        command=check_formats,
        font=("Segoe UI", 11),
        bg="#e5e7eb",
        fg="#111827",
        activebackground="#d1d5db",
        activeforeground="#111827",
        relief="flat",
        bd=0,
        cursor="hand2"
    )
    check_button.pack(fill="x", padx=34, pady=(0, 18), ipady=10)

    mode_title = tk.Label(
        card,
        text="Режим выбора качества",
        font=("Segoe UI", 10, "bold"),
        bg="#ffffff",
        fg="#374151",
        anchor="w"
    )
    mode_title.pack(fill="x", padx=34)

    mode_frame = tk.Frame(card, bg="#ffffff")
    mode_frame.pack(fill="x", padx=34, pady=(8, 14))

    quality_mode = tk.StringVar(value="simple")

    simple_radio = tk.Radiobutton(
        mode_frame,
        text="Обычный",
        variable=quality_mode,
        value="simple",
        command=on_quality_mode_change,
        font=("Segoe UI", 10),
        bg="#ffffff",
        fg="#111827",
        activebackground="#ffffff",
        activeforeground="#111827",
        selectcolor="#ffffff"
    )
    simple_radio.pack(side="left", padx=(0, 18))

    advanced_radio = tk.Radiobutton(
        mode_frame,
        text="Продвинутый",
        variable=quality_mode,
        value="advanced",
        command=on_quality_mode_change,
        font=("Segoe UI", 10),
        bg="#ffffff",
        fg="#111827",
        activebackground="#ffffff",
        activeforeground="#111827",
        selectcolor="#ffffff"
    )
    advanced_radio.pack(side="left")

    quality_label = tk.Label(
        card,
        text="Доступные качества",
        font=("Segoe UI", 11, "bold"),
        bg="#ffffff",
        fg="#374151",
        anchor="w"
    )
    quality_label.pack(fill="x", padx=34)

    quality_combo = ttk.Combobox(card, values=[], state="disabled", font=("Segoe UI", 10))
    quality_combo.pack(fill="x", padx=34, pady=(8, 18), ipady=6)

    folder_button = tk.Button(
        card,
        text="Выбрать папку",
        command=choose_folder,
        font=("Segoe UI", 11),
        bg="#e5e7eb",
        fg="#111827",
        activebackground="#d1d5db",
        activeforeground="#111827",
        relief="flat",
        bd=0,
        cursor="hand2"
    )
    folder_button.pack(fill="x", padx=34, pady=(0, 10), ipady=10)

    folder_label = tk.Label(
        card,
        text="Папка не выбрана",
        font=("Segoe UI", 10),
        bg="#ffffff",
        fg="#1f2937",
        anchor="center",
        justify="center"
    )
    folder_label.pack(fill="x", padx=34, pady=(0, 14))

    open_folder_button = tk.Button(
        card,
        text="Открыть папку",
        command=open_folder,
        font=("Segoe UI", 11),
        bg="#e5e7eb",
        fg="#111827",
        activebackground="#d1d5db",
        activeforeground="#111827",
        relief="flat",
        bd=0,
        cursor="hand2"
    )
    open_folder_button.pack(fill="x", padx=34, pady=(0, 18), ipady=10)

    download_button = tk.Button(
        card,
        text="Скачать",
        command=start_download,
        font=("Segoe UI", 12, "bold"),
        bg="#93c5fd",
        fg="white",
        activebackground="#93c5fd",
        activeforeground="white",
        relief="flat",
        bd=0,
        cursor="hand2",
        state="disabled"
    )
    download_button.pack(fill="x", padx=34, pady=(0, 10), ipady=11)

    cancel_button = tk.Button(
        card,
        text="Отмена",
        command=cancel_download,
        font=("Segoe UI", 12, "bold"),
        bg="#f3b0b0",
        fg="white",
        activebackground="#f3b0b0",
        activeforeground="white",
        relief="flat",
        bd=0,
        cursor="hand2",
        state="disabled"
    )
    cancel_button.pack(fill="x", padx=34, pady=(0, 16), ipady=11)

    progress_bar = ttk.Progressbar(
        card,
        orient="horizontal",
        mode="determinate",
        maximum=100,
        style="Custom.Horizontal.TProgressbar"
    )
    progress_bar.pack(fill="x", padx=34, pady=(0, 10))

    status_label = tk.Label(
        card,
        text="Готов к работе",
        font=("Segoe UI", 10),
        bg="#ffffff",
        fg="#6b7280"
    )
    status_label.pack(fill="x", padx=34, pady=(0, 14))

    save_log_button = tk.Button(
        card,
        text="Сохранить лог",
        command=save_log_to_file,
        font=("Segoe UI", 10),
        bg="#e5e7eb",
        fg="#111827",
        activebackground="#d1d5db",
        activeforeground="#111827",
        relief="flat",
        bd=0,
        cursor="hand2"
    )
    save_log_button.pack(fill="x", padx=34, pady=(6, 24), ipady=8)

    reset_progressbar()
    set_state(APP_STATE_IDLE)
    append_log(LOG_INFO, "Приложение запущено")
    root.after(100, process_ui_queue)
    root.mainloop()


if __name__ == "__main__":
    build_ui()
