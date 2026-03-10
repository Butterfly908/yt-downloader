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

CURRENT_LANG = "en"

TEXTS = {
    "ru": {
        "app_title": "YT downloader",
        "title_label": "YT Downloader",
        "video_url": "Ссылка на видео",
        "check_qualities": "Проверить качества",
        "quality_mode_title": "Режим выбора качества",
        "simple_mode": "Обычный",
        "advanced_mode": "Продвинутый",
        "available_qualities": "Доступные качества",
        "choose_folder": "Выбрать папку",
        "folder_not_selected": "Папка не выбрана",
        "open_folder": "Открыть папку",
        "download": "Скачать",
        "cancel": "Отмена",
        "save_log": "Сохранить лог",
        "ready_to_work": "Готов к работе",
        "loading_qualities": "Получение доступных качеств...",
        "qualities_loaded": "Качества загружены",
        "qualities_error": "Ошибка получения качеств",
        "preparing": "Подготовка...",
        "downloading_status": "Скачивание...",
        "processing_file": "Обработка файла...",
        "done": "Готово!",
        "download_cancelled": "Загрузка отменена",
        "error_status": "Ошибка",
        "stopping_download": "Остановка загрузки...",
        "audio_only": "Только аудио (mp3)",
        "untitled": "Без названия",
        "log_title": "Лог",
        "log_empty": "Лог пуст",
        "save_log_title": "Сохранить лог",
        "success_title": "Успех",
        "log_saved": "Лог сохранён",
        "error_title": "Ошибка",
        "warning_title": "Внимание",
        "choose_folder_first": "Сначала выберите папку",
        "folder_not_found": "Папка не найдена",
        "enter_video_url": "Введите ссылку на видео",
        "choose_save_folder": "Выберите папку для сохранения",
        "click_check_first": "Сначала нажмите 'Проверить качества'",
        "select_available_quality": "Выберите доступное качество",
        "download_completed": "Скачивание завершено",
        "download_stopped": "Загрузка остановлена",
        "unknown_error": "Неизвестная ошибка",
        "ffmpeg_missing_title": "Не найден FFmpeg",
        "ffmpeg_missing_message": "FFmpeg не найден. Для объединения видео и аудио нужен ffmpeg.\\n\\nЕсли вы запускаете собранную версию, убедитесь, что ffmpeg.exe и ffprobe.exe лежат рядом с YT downloader.exe.\\n\\nЕсли вы запускаете из исходников, установите FFmpeg или добавьте его в PATH.",
        "log_app_started": "Приложение запущено",
        "log_folder_selected": "Выбрана папка: {folder}",
        "log_folder_opened": "Открыта папка: {folder}",
        "log_quality_mode_changed": "Режим качества переключен: {mode}",
        "log_start_checking": "Старт проверки качеств",
        "log_requested_quality_check": "Запрошена проверка качеств: {url}",
        "log_video_info_received": "Получена информация о видео: {title}",
        "log_formats_found": "Качеств найдено: обычных={simple_count}, продвинутых={advanced_count}",
        "log_formats_error": "Ошибка получения качеств: {error}",
        "log_download_button_pressed": "Нажата кнопка Скачать",
        "log_download_started": "Старт загрузки: {url}",
        "log_save_folder": "Папка сохранения: {folder}",
        "log_selected_format": "Выбранный формат: {format_}",
        "log_prepared_path": "Подготовлен путь: {path}",
        "log_download_stage_finished": "Этап скачивания завершён: {filename}",
        "log_download_success": "Загрузка успешно завершена",
        "log_download_cancelled_after_worker": "Загрузка отменена после завершения worker",
        "log_user_cancelled": "Пользователь отменил загрузку",
        "log_download_error": "Ошибка загрузки: {error}",
        "log_cancel_button_pressed": "Нажата кнопка Отмена",
    },
    "en": {
        "app_title": "YT downloader",
        "title_label": "YT Downloader",
        "video_url": "Video URL",
        "check_qualities": "Check qualities",
        "quality_mode_title": "Quality selection mode",
        "simple_mode": "Simple",
        "advanced_mode": "Advanced",
        "available_qualities": "Available qualities",
        "choose_folder": "Choose folder",
        "folder_not_selected": "No folder selected",
        "open_folder": "Open folder",
        "download": "Download",
        "cancel": "Cancel",
        "save_log": "Save log",
        "ready_to_work": "Ready",
        "loading_qualities": "Loading available qualities...",
        "qualities_loaded": "Qualities loaded",
        "qualities_error": "Failed to load qualities",
        "preparing": "Preparing...",
        "downloading_status": "Downloading...",
        "processing_file": "Processing file...",
        "done": "Done!",
        "download_cancelled": "Download cancelled",
        "error_status": "Error",
        "stopping_download": "Stopping download...",
        "audio_only": "Audio only (mp3)",
        "untitled": "Untitled",
        "log_title": "Log",
        "log_empty": "Log is empty",
        "save_log_title": "Save log",
        "success_title": "Success",
        "log_saved": "Log saved",
        "error_title": "Error",
        "warning_title": "Warning",
        "choose_folder_first": "Please choose a folder first",
        "folder_not_found": "Folder not found",
        "enter_video_url": "Enter a video URL",
        "choose_save_folder": "Choose a save folder",
        "click_check_first": "Click 'Check qualities' first",
        "select_available_quality": "Select an available quality",
        "download_completed": "Download completed",
        "download_stopped": "Download stopped",
        "unknown_error": "Unknown error",
        "ffmpeg_missing_title": "FFmpeg not found",
        "ffmpeg_missing_message": "FFmpeg was not found. FFmpeg is required to merge video and audio streams.\\n\\nIf you are running the packaged build, make sure ffmpeg.exe and ffprobe.exe are placed next to YT downloader.exe.\\n\\nIf you are running from source, install FFmpeg or add it to PATH.",
        "log_app_started": "Application started",
        "log_folder_selected": "Folder selected: {folder}",
        "log_folder_opened": "Folder opened: {folder}",
        "log_quality_mode_changed": "Quality mode changed: {mode}",
        "log_start_checking": "Started checking qualities",
        "log_requested_quality_check": "Requested quality check: {url}",
        "log_video_info_received": "Video info received: {title}",
        "log_formats_found": "Formats found: simple={simple_count}, advanced={advanced_count}",
        "log_formats_error": "Failed to load qualities: {error}",
        "log_download_button_pressed": "Download button pressed",
        "log_download_started": "Download started: {url}",
        "log_save_folder": "Save folder: {folder}",
        "log_selected_format": "Selected format: {format_}",
        "log_prepared_path": "Prepared path: {path}",
        "log_download_stage_finished": "Download stage finished: {filename}",
        "log_download_success": "Download completed successfully",
        "log_download_cancelled_after_worker": "Download cancelled after worker finished",
        "log_user_cancelled": "User cancelled the download",
        "log_download_error": "Download error: {error}",
        "log_cancel_button_pressed": "Cancel button pressed",
    }
}

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


def tr(key, **kwargs):
    text = TEXTS.get(CURRENT_LANG, {}).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def bundled_bin_path(filename):
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)


def get_ffmpeg_location():
    ffmpeg_path = bundled_bin_path("ffmpeg.exe")
    ffprobe_path = bundled_bin_path("ffprobe.exe")
    if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
        return os.path.dirname(ffmpeg_path)
    return None


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
        messagebox.showinfo(tr("log_title"), tr("log_empty"))
        return

    path = filedialog.asksaveasfilename(
        title=tr("save_log_title"),
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not path:
        return

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(app_log_lines))
        messagebox.showinfo(tr("success_title"), tr("log_saved"))
    except Exception as e:
        messagebox.showerror(tr("error_title"), str(e))


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
    folder = filedialog.askdirectory(title=tr("choose_folder"))
    if folder:
        save_folder = folder
        folder_label.config(text=save_folder)
        log_message(LOG_INFO, tr("log_folder_selected", folder=save_folder))


def open_folder():
    if not save_folder:
        messagebox.showwarning(tr("warning_title"), tr("choose_folder_first"))
        return
    if os.path.exists(save_folder):
        os.startfile(save_folder)
        log_message(LOG_INFO, tr("log_folder_opened", folder=save_folder))
    else:
        messagebox.showerror(tr("error_title"), tr("folder_not_found"))


def on_quality_mode_change():
    if formats_map_simple or formats_map_advanced:
        refresh_quality_list()
        log_message(LOG_INFO, tr("log_quality_mode_changed", mode=quality_mode.get()))


def load_formats_worker(url):
    log_message(LOG_INFO, tr("log_start_checking"))
    log_message(LOG_INFO, "-" * 70)
    log_message(LOG_INFO, tr("log_requested_quality_check", url=url))

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
        title = info.get("title", tr("untitled"))
        log_message(LOG_INFO, tr("log_video_info_received", title=title))

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
                advanced_map[tr("audio_only")] = "bestaudio"
                audio_added = True

        simple_map = {}
        for height in sorted(simple_candidates.keys(), reverse=True):
            item = simple_candidates[height]
            simple_map[item["label"]] = item["format_id"]

        if audio_added:
            simple_map[tr("audio_only")] = "bestaudio"

        advanced_map = dict(
            sorted(
                advanced_map.items(),
                key=lambda item: (
                    9999 if item[0] == tr("audio_only") else -extract_height(item[0])
                )
            )
        )

        log_message(
            LOG_INFO,
            tr("log_formats_found", simple_count=len(simple_map), advanced_count=len(advanced_map))
        )
        post_ui_message(MSG_FORMATS_LOADED, simple_map=simple_map, advanced_map=advanced_map)

    except Exception as e:
        log_message(LOG_ERROR, tr("log_formats_error", error=e))
        post_ui_message(MSG_FORMATS_ERROR, error_text=str(e))


def check_formats():
    global is_checking, check_thread

    url = url_entry.get().strip()
    if url == "":
        messagebox.showerror(tr("error_title"), tr("enter_video_url"))
        return

    if app_state != APP_STATE_IDLE:
        return

    is_checking = True
    quality_combo.set("")
    quality_combo["values"] = []
    reset_progressbar()
    status_label.config(text=tr("loading_qualities"))
    set_state(APP_STATE_CHECKING)

    check_thread = threading.Thread(target=load_formats_worker, args=(url,), daemon=True)
    check_thread.start()


def download_worker(url, save_path, selected_format):
    downloaded_filename = None
    prepared_name = None

    def hook(d):
        nonlocal downloaded_filename

        if cancel_event.is_set():
            raise DownloadCancelled(tr("download_cancelled"))

        filename = d.get("filename")
        if filename:
            downloaded_filename = filename

        status = d.get("status")

        if status == "downloading":
            percent_value = None
            text = tr("downloading_status")

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
                if CURRENT_LANG == "ru":
                    text = f"Скачивание... {percent_str} | Скорость: {speed} | Осталось: {eta}"
                else:
                    text = f"Downloading... {percent_str} | Speed: {speed} | ETA: {eta}"

            post_ui_message(MSG_PROGRESS, text=text, percent=percent_value)

        elif status == "finished":
            if filename:
                downloaded_filename = filename
            log_message(LOG_INFO, tr("log_download_stage_finished", filename=filename if filename else tr("untitled")))
            post_ui_message(MSG_STAGE, text=tr("processing_file"))

    logger = YTDLPLogger()
    ffmpeg_location = get_ffmpeg_location()

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

    if ffmpeg_location:
        ydl_opts["ffmpeg_location"] = ffmpeg_location

    try:
        log_message(LOG_INFO, tr("log_download_button_pressed"))
        log_message(LOG_INFO, "-" * 70)
        log_message(LOG_INFO, tr("log_download_started", url=url))
        log_message(LOG_INFO, tr("log_save_folder", folder=save_path))
        log_message(LOG_INFO, tr("log_selected_format", format_=selected_format))
        post_ui_message(MSG_STAGE, text=tr("preparing"))

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            prepared_name = ydl.prepare_filename(info)
            log_message(LOG_INFO, tr("log_prepared_path", path=prepared_name))

            if cancel_event.is_set():
                raise DownloadCancelled(tr("download_cancelled"))

            ydl.download([url])

        if cancel_event.is_set():
            cleanup_temp_by_filename(downloaded_filename)
            cleanup_temp_by_filename(prepared_name)
            log_message(LOG_WARNING, tr("log_download_cancelled_after_worker"))
            post_ui_message(MSG_CANCELLED)
            return

        log_message(LOG_INFO, tr("log_download_success"))
        post_ui_message(MSG_FINISHED)

    except DownloadCancelled:
        cleanup_temp_by_filename(downloaded_filename)
        cleanup_temp_by_filename(prepared_name)
        log_message(LOG_WARNING, tr("log_user_cancelled"))
        post_ui_message(MSG_CANCELLED)

    except Exception as e:
        cleanup_temp_by_filename(downloaded_filename)
        cleanup_temp_by_filename(prepared_name)
        log_message(LOG_ERROR, tr("log_download_error", error=e))
        post_ui_message(MSG_ERROR, error_text=str(e))


def start_download():
    global download_thread

    url = url_entry.get().strip()
    selected_label = quality_combo.get()

    if url == "":
        messagebox.showerror(tr("error_title"), tr("enter_video_url"))
        return

    if save_folder == "":
        messagebox.showerror(tr("error_title"), tr("choose_save_folder"))
        return

    if selected_label == "":
        messagebox.showerror(tr("error_title"), tr("click_check_first"))
        return

    if selected_label not in formats_map:
        messagebox.showerror(tr("error_title"), tr("select_available_quality"))
        return

    if app_state != APP_STATE_IDLE:
        return

    cancel_event.clear()
    reset_progressbar()
    set_progress_indeterminate("#3b82f6")
    status_label.config(text=tr("preparing"))
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
    log_message(LOG_WARNING, tr("log_cancel_button_pressed"))
    status_label.config(text=tr("stopping_download"))
    set_progress_indeterminate("#ef4444")
    set_state(APP_STATE_CANCELLING)


def handle_formats_loaded(message):
    global formats_map_simple, formats_map_advanced, is_checking

    is_checking = False
    formats_map_simple = message["simple_map"]
    formats_map_advanced = message["advanced_map"]

    refresh_quality_list()
    status_label.config(text=tr("qualities_loaded"))
    reset_progressbar()
    set_state(APP_STATE_IDLE)


def handle_formats_error(message):
    global is_checking

    is_checking = False
    quality_combo.set("")
    quality_combo["values"] = []
    reset_progressbar()
    status_label.config(text=tr("qualities_error"))
    set_state(APP_STATE_IDLE)
    download_button.config(state="disabled", bg="#93c5fd", activebackground="#93c5fd")
    messagebox.showerror(tr("error_title"), message.get("error_text", tr("unknown_error")))


def handle_progress(message):
    text = message.get("text", tr("downloading_status"))
    percent = message.get("percent")

    status_label.config(text=text)

    if percent is not None:
        set_progress_determinate(int(percent), "#3b82f6")
    else:
        set_progress_indeterminate("#3b82f6")


def handle_stage(message):
    text = message.get("text", tr("processing_file"))
    status_label.config(text=text)
    set_progress_indeterminate("#3b82f6")


def handle_finished():
    set_progress_determinate(100, "#22c55e")
    status_label.config(text=tr("done"))
    set_state(APP_STATE_IDLE)
    messagebox.showinfo(tr("success_title"), tr("download_completed"))


def handle_cancelled():
    set_progress_determinate(0, "#ef4444")
    status_label.config(text=tr("download_cancelled"))
    set_state(APP_STATE_IDLE)
    messagebox.showinfo(tr("cancel"), tr("download_stopped"))


def handle_error(message):
    error_text = message.get("error_text", tr("unknown_error"))
    set_progress_determinate(0, "#ef4444")
    status_label.config(text=tr("error_status"))
    set_state(APP_STATE_IDLE)

    error_lower = error_text.lower()
    if "ffmpeg is not installed" in error_lower or "ffmpeg not found" in error_lower:
        messagebox.showerror(tr("ffmpeg_missing_title"), tr("ffmpeg_missing_message"))
    else:
        messagebox.showerror(tr("error_title"), error_text)


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
    root.title(tr("app_title"))
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
        text=tr("title_label"),
        font=("Segoe UI", 28, "bold"),
        bg="#ffffff",
        fg="#111827"
    )
    title_label.pack(pady=(18, 28))

    url_label = tk.Label(
        card,
        text=tr("video_url"),
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
        text=tr("check_qualities"),
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
        text=tr("quality_mode_title"),
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
        text=tr("simple_mode"),
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
        text=tr("advanced_mode"),
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
        text=tr("available_qualities"),
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
        text=tr("choose_folder"),
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
        text=tr("folder_not_selected"),
        font=("Segoe UI", 10),
        bg="#ffffff",
        fg="#1f2937",
        anchor="center",
        justify="center"
    )
    folder_label.pack(fill="x", padx=34, pady=(0, 14))

    open_folder_button = tk.Button(
        card,
        text=tr("open_folder"),
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
        text=tr("download"),
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
        text=tr("cancel"),
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
        text=tr("ready_to_work"),
        font=("Segoe UI", 10),
        bg="#ffffff",
        fg="#6b7280"
    )
    status_label.pack(fill="x", padx=34, pady=(0, 14))

    save_log_button = tk.Button(
        card,
        text=tr("save_log"),
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
    append_log(LOG_INFO, tr("log_app_started"))
    root.after(100, process_ui_queue)
    root.mainloop()


if __name__ == "__main__":
    build_ui()
