import tkinter as tk
from tkinter import ttk, messagebox, font, scrolledtext
import subprocess
import sys
import os
import ctypes
from datetime import datetime, timedelta, time as dt_time 
import logging
import traceback
import json 

# --- הגדרות ---
TASK_NAME = "DailyAutoRestartByMyScript"
NOTIFICATION_TASK_NAME = "DailyAutoRestartNotificationByMyScript"
LOG_FILE_NAME = "restart_scheduler.log"
CONFIG_FILE_NAME = "restart_scheduler_config.json"

DEFAULT_NOTIFICATION_MESSAGE = "מחשב זה יופעל מחדש בעוד דקה.\nשמור כל קובץ פתוח למנוע אובדן מידע."

# --- הגדרת יומן רישום (Logging) ---
def setup_logging():
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), LOG_FILE_NAME)
    logger_obj = logging.getLogger('RestartScheduler') 
    if not logger_obj.handlers:
        logger_obj.setLevel(logging.INFO)
        try:
            fh = logging.FileHandler(log_file_path, encoding='utf-8')
            fh.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            fh.setFormatter(formatter)
            logger_obj.addHandler(fh)
            logger_obj.info("Logging initialized.")
        except Exception as e:
            print(f"Error setting up logger: {e}")
            return None
    return logger_obj

logger = setup_logging()

def log_info(message):
    if logger: logger.info(message)
    else: print(f"INFO: {message}")

def log_warning(message):
    if logger: logger.warning(message)
    else: print(f"WARNING: {message}")

def log_error(message, exc_info=False):
    if logger: logger.error(message, exc_info=exc_info)
    else: print(f"ERROR: {message}")

def log_exception(message):
    if logger: logger.exception(message)
    else: print(f"EXCEPTION: {message}\n{traceback.format_exc()}")


# --- פונקציות עזר (הרשאות, קונפיגורציה) ---
def is_admin():
    try:
        is_admin_flag = ctypes.windll.shell32.IsUserAnAdmin()
        log_info(f"IsUserAnAdmin check result: {is_admin_flag}")
        return is_admin_flag
    except Exception as e:
        log_exception(f"Error checking admin status: {e}")
        return False

def run_as_admin():
    log_warning("Attempting to re-run script with administrator privileges.")
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    except Exception as e:
        log_exception(f"Failed to elevate privileges: {e}")
        messagebox.showerror("שגיאת הרשאות", f"לא ניתן היה להפעיל מחדש עם הרשאות מנהל:\n{e}")

def get_config_path():
    return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), CONFIG_FILE_NAME)

def load_config():
    config_path = get_config_path()
    default_config = {
        "notification_message": DEFAULT_NOTIFICATION_MESSAGE,
        "user_lockout_schedules": {} 
    }
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                if "user_lockout_schedules" not in config: 
                    config["user_lockout_schedules"] = {}
                log_info(f"Loaded config: {config}")
                return config
    except Exception as e:
        log_exception(f"Error loading config file '{config_path}': {e}")
    return default_config

def save_config(config_data):
    config_path = get_config_path()
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        log_info(f"Saved config data: {config_data}")
    except Exception as e:
        log_exception(f"Error saving config file '{config_path}': {e}")
        messagebox.showerror("שגיאת שמירה", f"לא ניתן היה לשמור את ההגדרות:\n{e}")

# --- מחלקת ה-GUI ---
class RestartSchedulerApp:
    def __init__(self, master):
        self.master = master
        log_info("Initializing GUI.")
        master.title("CobaltScreenTime")
        master.geometry("600x600") # Reduced height a bit due to less controls

        self.config = load_config()

        try:
            master.tk.call('tk', 'scaling', 1.1)
        except:
            pass

        self.custom_font = font.Font(family="Arial", size=10)
        self.label_font = font.Font(family="Arial", size=10, weight="bold")

        self.notebook = ttk.Notebook(master)
        
        self.restart_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.restart_tab, text='הפעלה מחדש')
        self.create_restart_tab_content()

        self.lockout_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.lockout_tab, text='נעילת משתמשים')
        self.create_lockout_tab_content()
        
        self.notebook.pack(expand=1, fill="both")

        self.status_label = ttk.Label(master, text="", font=self.custom_font, foreground="blue", wraplength=580, justify=tk.CENTER)
        self.status_label.pack(pady=10, fill="x", padx=10)

        log_file_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), LOG_FILE_NAME)
        self.log_label = ttk.Label(master, text=f"יומן רישום נשמר ב:\n{log_file_path}", font=("Arial", 8), foreground="gray", justify=tk.CENTER)
        self.log_label.pack(pady=5, side=tk.BOTTOM, fill="x", padx=10)

        style = ttk.Style()
        style.configure("Accent.TButton", font=self.custom_font, padding=5)
        style.configure("TButton", font=self.custom_font, padding=5)
        style.configure("TLabel", font=self.custom_font)
        style.configure("TCombobox", font=self.custom_font)
        style.configure("TLabelframe.Label", font=self.label_font)
        style.configure("TLabelframe", font=self.custom_font)
        style.configure("TNotebook.Tab", font=self.custom_font)

        self.check_existing_restart_task() 
        log_info("GUI Initialized successfully.")

    def create_restart_tab_content(self):
        # This function content remains the same as previous correct version
        time_frame_outer = ttk.LabelFrame(self.restart_tab, text="הגדרת שעת הפעלה מחדש", padding=(10, 5))
        time_frame_outer.pack(pady=10, padx=0, fill="x")

        self.label_time = ttk.Label(time_frame_outer, text="בחר שעת הפעלה מחדש יומית:", font=self.custom_font)
        self.label_time.pack(pady=(0,5), anchor="e")

        time_frame_inner = ttk.Frame(time_frame_outer)
        time_frame_inner.pack() 

        self.hour_var = tk.StringVar(self.master) 
        self.minute_var = tk.StringVar(self.master) 
        self.hour_var.set("02")
        self.minute_var.set("00")

        hours = [f"{h:02d}" for h in range(24)]
        minutes = [f"{m:02d}" for m in range(60)]
        
        self.minute_spinbox = ttk.Combobox(time_frame_inner, textvariable=self.minute_var, values=minutes, width=3, state="readonly", font=self.custom_font)
        self.minute_spinbox.pack(side=tk.RIGHT, padx=(0,5)) 

        self.separator_label = ttk.Label(time_frame_inner, text=":", font=self.custom_font)
        self.separator_label.pack(side=tk.RIGHT)

        self.hour_spinbox = ttk.Combobox(time_frame_inner, textvariable=self.hour_var, values=hours, width=3, state="readonly", font=self.custom_font)
        self.hour_spinbox.pack(side=tk.RIGHT, padx=(5,0)) 

        message_frame = ttk.LabelFrame(self.restart_tab, text="הגדרת הודעת התראה להפעלה מחדש", padding=(10, 5))
        message_frame.pack(pady=10, padx=0, fill="x")

        self.label_message_restart = ttk.Label(message_frame, text="טקסט ההודעה (תוצג דקה לפני ההפעלה מחדש):", font=self.custom_font)
        self.label_message_restart.pack(pady=(0,5), anchor="e")

        self.notification_message_text = scrolledtext.ScrolledText(message_frame, width=50, height=3, font=self.custom_font, wrap=tk.WORD)
        self.notification_message_text.pack(fill="x", expand=True)
        self.notification_message_text.insert(tk.END, self.config.get("notification_message", DEFAULT_NOTIFICATION_MESSAGE))

        button_frame_restart = ttk.Frame(self.restart_tab)
        button_frame_restart.pack(pady=20)

        self.set_button_restart = ttk.Button(button_frame_restart, text="קבע הפעלה מחדש", command=self.set_restart_time, style="Accent.TButton")
        self.set_button_restart.pack(side=tk.RIGHT, padx=5)

        self.cancel_button_restart = ttk.Button(button_frame_restart, text="בטל הפעלה מחדש מתוזמנת", command=self.cancel_restart_task)
        self.cancel_button_restart.pack(side=tk.RIGHT, padx=5)


    def create_lockout_tab_content(self):
        lockout_main_frame = ttk.Frame(self.lockout_tab)
        lockout_main_frame.pack(fill="both", expand=True)

        user_select_frame = ttk.LabelFrame(lockout_main_frame, text="בחירת משתמש לניהול נעילה", padding=(10,5))
        user_select_frame.pack(pady=5, padx=0, fill="x")

        ttk.Label(user_select_frame, text="בחר משתמש:", font=self.custom_font).pack(side=tk.RIGHT, padx=(0,10), pady=5)
        self.lockout_user_var = tk.StringVar(self.master)
        
        local_users = self.get_local_users()
        if not local_users:
            local_users = ["(לא נמצאו משתמשים)"]
            log_warning("Could not retrieve local users for lockout tab.")
            
        self.lockout_user_combo = ttk.Combobox(user_select_frame, textvariable=self.lockout_user_var, values=local_users, state="readonly", font=self.custom_font, width=25)
        self.lockout_user_combo.pack(side=tk.RIGHT, pady=5)
        if local_users and local_users[0] != "(לא נמצאו משתמשים)":
            self.lockout_user_var.set(local_users[0])
        
        self.lockout_user_combo.bind("<<ComboboxSelected>>", self.load_user_lockout_settings_event)

        self.lockout_settings_frame = ttk.LabelFrame(lockout_main_frame, text="הגדרות נעילה עבור משתמש נבחר", padding=(10,5))
        self.lockout_settings_frame.pack(pady=10, padx=0, fill="x")

        self.lockout_enabled_var = tk.BooleanVar(self.master)
        self.lockout_enable_check = ttk.Checkbutton(self.lockout_settings_frame, text="אפשר נעילה מתוזמנת עבור משתמש זה", variable=self.lockout_enabled_var, command=self.toggle_lock_time_fields_state)
        self.lockout_enable_check.grid(row=0, column=0, columnspan=2, sticky="e", pady=5) # Adjusted columnspan

        # Lock Start Time (Hour only)
        ttk.Label(self.lockout_settings_frame, text="שעת התחלת נעילה (שעה עגולה):", font=self.custom_font).grid(row=1, column=1, sticky="e", padx=5, pady=5)
        self.lockout_start_hour_var = tk.StringVar(self.master, value="22")
        self.lockout_start_hour_combo = ttk.Combobox(self.lockout_settings_frame, textvariable=self.lockout_start_hour_var, values=[f"{h:02d}" for h in range(24)], width=3, state="disabled", font=self.custom_font)
        self.lockout_start_hour_combo.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        # Lock End Time (Hour only)
        ttk.Label(self.lockout_settings_frame, text="שעת סיום נעילה (שעה עגולה):", font=self.custom_font).grid(row=2, column=1, sticky="e", padx=5, pady=5)
        self.lockout_end_hour_var = tk.StringVar(self.master, value="07")
        self.lockout_end_hour_combo = ttk.Combobox(self.lockout_settings_frame, textvariable=self.lockout_end_hour_var, values=[f"{h:02d}" for h in range(24)], width=3, state="disabled", font=self.custom_font)
        self.lockout_end_hour_combo.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        lockout_button_frame = ttk.Frame(lockout_main_frame)
        lockout_button_frame.pack(pady=20)

        self.apply_lockout_button = ttk.Button(lockout_button_frame, text="החל הגדרות נעילה", command=self.apply_user_lockout_settings, style="Accent.TButton")
        self.apply_lockout_button.pack(side=tk.RIGHT, padx=5)

        self.clear_lockout_button = ttk.Button(lockout_button_frame, text="נקה הגדרות נעילה למשתמש זה", command=self.clear_user_lockout_settings)
        self.clear_lockout_button.pack(side=tk.RIGHT, padx=5)

        self.load_user_lockout_settings() 
        self.toggle_lock_time_fields_state()


    def get_startupinfo(self):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return startupinfo

    def get_local_users(self):
        # This function content remains the same
        log_info("Attempting to retrieve local users.")
        users = []
        try:
            process = subprocess.Popen(["net", "user"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp862', errors='replace', startupinfo=self.get_startupinfo())
            stdout, stderr = process.communicate(timeout=10)

            if process.returncode == 0:
                lines = stdout.splitlines()
                user_lines_started = False
                for line in lines:
                    if line.strip().startswith("---"):
                        user_lines_started = True
                        continue
                    if "The command completed successfully" in line :
                        user_lines_started = False 
                        break 
                    if not user_lines_started or not line.strip():
                        continue
                    
                    current_line_users = [u.strip() for u in line.split('  ') if u.strip()] 
                    users.extend(current_line_users)
                
                excluded_users = ["Administrator", "Guest", "DefaultAccount", "WDAGUtilityAccount", "SYSTEM", "LOCAL SERVICE", "NETWORK SERVICE", "HomeGroupUser$"]
                users = sorted(list(set([u for u in users if u and u not in excluded_users and not u.startswith("ASPNET")])))
                log_info(f"Retrieved and filtered local users: {users}")
            else:
                log_error(f"Failed to retrieve users using 'net user'. Return code: {process.returncode}, Stderr: {stderr.strip()}")
        except Exception as e:
            log_exception("Exception while retrieving local users.")
        
        return users if users else []


    def load_user_lockout_settings_event(self, event=None): 
        self.load_user_lockout_settings()

    def load_user_lockout_settings(self): 
        username = self.lockout_user_var.get()
        if not username or username == "(לא נמצאו משתמשים)":
            self.lockout_enabled_var.set(False)
            self.lockout_start_hour_var.set("22")
            self.lockout_end_hour_var.set("07")
        else:
            log_info(f"Loading lockout settings for user: {username}")
            if "user_lockout_schedules" not in self.config:
                self.config["user_lockout_schedules"] = {}
            user_settings = self.config.get("user_lockout_schedules", {}).get(username, {})
            
            self.lockout_enabled_var.set(user_settings.get("enabled", False))
            self.lockout_start_hour_var.set(user_settings.get("lock_start_hh", "22"))
            self.lockout_end_hour_var.set(user_settings.get("lock_end_hh", "07"))
        
        self.toggle_lock_time_fields_state()

    def toggle_lock_time_fields_state(self): 
        state = tk.NORMAL if self.lockout_enabled_var.get() else tk.DISABLED
        widgets_to_toggle = [
            self.lockout_start_hour_combo,
            self.lockout_end_hour_combo,
        ]
        for widget in widgets_to_toggle:
            if widget: 
                widget.config(state=state)

    def to_12_hour_ampm(self, hour_24_str): # Expects string like "07" or "22"
        hour_24 = int(hour_24_str)
        am_pm = "AM"
        if hour_24 >= 12:
            am_pm = "PM"
        if hour_24 == 0: 
            hour_12 = 12
        elif hour_24 > 12:
            hour_12 = hour_24 - 12
        else:
            hour_12 = hour_24
        return f"{hour_12:d}:00{am_pm}"

    def apply_user_lockout_settings(self):
        username = self.lockout_user_var.get()
        if not username or username == "(לא נמצאו משתמשים)":
            messagebox.showerror("שגיאה", "יש לבחור משתמש תחילה.")
            return

        is_enabled = self.lockout_enabled_var.get()
        command_args = [] 
        
        start_h_ui_24 = self.lockout_start_hour_var.get() 
        end_h_ui_24 = self.lockout_end_hour_var.get()
        
        if is_enabled:
            try:
                start_time_obj = dt_time(int(start_h_ui_24), 0)
                end_time_obj = dt_time(int(end_h_ui_24), 0)
            except ValueError:
                messagebox.showerror("שגיאה", "פורמט שעות הנעילה אינו תקין (שעה לא חוקית).")
                log_error(f"Invalid lockout time (hour) format: Start {start_h_ui_24}, End {end_h_ui_24}")
                return

            times_parameter_value = "" 

            start_lock_timestr_ampm = self.to_12_hour_ampm(start_h_ui_24)
            end_lock_timestr_ampm = self.to_12_hour_ampm(end_h_ui_24)
            
            if start_time_obj == end_time_obj:
                times_parameter_value = "" 
                log_info(f"Calculated lockout for {username}: Full 24-hour lockout (no logon times).")
            elif end_time_obj < start_time_obj: 
                times_parameter_value = f"M-Su,{end_lock_timestr_ampm}-{start_lock_timestr_ampm}"
                log_info(f"Calculated lockout for {username}: Spans midnight. Times value: {times_parameter_value}")
            else: # end_time_obj > start_time_obj
                allowed_range1_start_ampm = self.to_12_hour_ampm("00") # 12:00AM
                allowed_range1_end_ampm = start_lock_timestr_ampm
                
                allowed_range2_start_ampm = end_lock_timestr_ampm
                allowed_range2_end_ampm = self.to_12_hour_ampm("00") # Represents end of day as start of next day 12:00AM

                range1_str = f"M-Su,{allowed_range1_start_ampm}-{allowed_range1_end_ampm}"
                range2_str = f"M-Su,{allowed_range2_start_ampm}-{allowed_range2_end_ampm}"

                if start_time_obj == dt_time(0, 0): 
                    times_parameter_value = range2_str
                elif end_time_obj == dt_time(0,0) and start_time_obj != end_time_obj : 
                    times_parameter_value = range1_str
                else:
                    times_parameter_value = f"{range1_str};{range2_str}"
                log_info(f"Calculated lockout for {username}: Within day. Times value: {times_parameter_value}")
            
            command_args = ["net", "user", username, f"/times:{times_parameter_value}"]
        else: 
            command_args = ["net", "user", username, "/times:ALL"]
            log_info(f"Lockout for {username} is disabled. Setting logon times to ALL.")

        log_info(f"Applying lockout for {username}. Command: {' '.join(command_args)}")
        success, msg = self._run_command(command_args)
        
        if success:
            self.update_user_config_lockout(username, is_enabled, start_h_ui_24, "00", end_h_ui_24, "00")
            
            if is_enabled:
                messagebox.showinfo("הצלחה", f"הגדרות הנעילה עבור המשתמש {username} הוחלו.")
                self.status_label.config(text=f"הגדרות נעילה הוחלו עבור {username}.", foreground="green")
            else:
                messagebox.showinfo("הצלחה", f"נעילה מתוזמנת עבור המשתמש {username} בוטלה (שעות התחברות ללא הגבלה).")
                self.status_label.config(text=f"נעילה בוטלה עבור {username}.", foreground="green")
        else:
            messagebox.showerror("שגיאה", f"נכשל בהחלת הגדרות נעילה עבור {username}:\n{msg}")
            log_error(f"Failed to apply lockout for {username}: {msg}")
            self.status_label.config(text=f"שגיאה בהחלת נעילה עבור {username}.", foreground="red")

    def clear_user_lockout_settings(self):
        # This function content remains the same
        username = self.lockout_user_var.get()
        if not username or username == "(לא נמצאו משתמשים)":
            messagebox.showerror("שגיאה", "יש לבחור משתמש תחילה.")
            return
        
        self.lockout_enabled_var.set(False) 
        self.apply_user_lockout_settings() 

    def update_user_config_lockout(self, username, enabled, start_hh, start_mm, end_hh, end_mm):
        # This function content remains the same (start_mm, end_mm will be "00")
        if "user_lockout_schedules" not in self.config: 
            self.config["user_lockout_schedules"] = {}
        self.config["user_lockout_schedules"][username] = {
            "enabled": enabled,
            "lock_start_hh": start_hh,
            "lock_start_mm": "00", 
            "lock_end_hh": end_hh,
            "lock_end_mm": "00"    
        }
        save_config(self.config)
        log_info(f"Updated config for user {username} lockout: enabled={enabled}, start={start_hh}:00, end={end_hh}:00")


    def _run_command(self, command_parts, capture_output=True):
        # This function content remains the same
        command_str = " ".join(f'"{part}"' if " " in part else part for part in command_parts)
        log_info(f"Running command: {command_str}")
        try:
            startupinfo = self.get_startupinfo()

            if capture_output:
                process = subprocess.Popen(command_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp862', errors='replace', startupinfo=startupinfo, shell=False)
                stdout, stderr = process.communicate(timeout=15)
            else:
                process = subprocess.Popen(command_parts, startupinfo=startupinfo, shell=False)
                process.wait(timeout=15)
                stdout, stderr = "", ""

            log_info(f"Command return code: {process.returncode}")
            if stdout: log_info(f"Command stdout: {stdout.strip()}")
            if stderr and process.returncode != 0 : log_warning(f"Command stderr: {stderr.strip()}")

            if process.returncode == 0:
                log_info("Command executed successfully.")
                return True, stdout
            else:
                if "delete" in command_parts and ("ERROR: The specified task name" in stderr or "לא נמצאה" in stderr or "לא היתה מופעלת" in stderr):
                     log_warning(f"Task delete ignored error (not found): {stderr.strip()}")
                     return True, "Task not found, considered deleted."
                log_error(f"Command failed (code {process.returncode}): {stderr.strip()}")
                return False, f"Error (code {process.returncode}): {stderr.strip()}\nOutput: {stdout.strip()}"
        except subprocess.TimeoutExpired:
            log_error(f"Command '{command_str}' timed out.")
            return False, "Command timed out."
        except Exception as e:
            log_exception(f"Exception running command '{command_str}': {e}")
            return False, str(e)


    def set_restart_time(self):
        # This function content remains the same
        hour = self.hour_var.get()
        minute = self.minute_var.get()
        restart_time_str = f"{hour}:{minute}"
        
        custom_message = self.notification_message_text.get("1.0", tk.END).strip()
        if not custom_message:
            messagebox.showerror("שגיאה", "טקסט הודעת ההתראה להפעלה מחדש לא יכול להיות ריק.")
            return
        
        self.config["notification_message"] = custom_message
        save_config(self.config)

        log_info(f"Attempting to set restart time to {restart_time_str} with message: '{custom_message[:50]}...'")

        try:
            datetime.strptime(restart_time_str, "%H:%M")
        except ValueError:
            log_error(f"Invalid time format selected: {restart_time_str}")
            messagebox.showerror("שגיאה", "שעה לא חוקית.")
            return

        self.status_label.config(text="יוצר משימות הפעלה מחדש...", foreground="orange")
        self.master.update_idletasks()

        self.delete_task(TASK_NAME) 
        self.delete_task(NOTIFICATION_TASK_NAME)

        log_info(f"Creating main restart task '{TASK_NAME}' for {restart_time_str}.")
        command_restart = [
            "schtasks", "/create", "/tn", TASK_NAME,
            "/tr", "shutdown /r /f /t 0", "/sc", "DAILY", "/st", restart_time_str,
            "/ru", "SYSTEM", "/f"
        ]
        success_restart, message_restart = self._run_command(command_restart)

        if not success_restart:
            log_error(f"Failed to create restart task: {message_restart}")
            self.status_label.config(text=f"שגיאה ביצירת משימת הפעלה מחדש:\n{message_restart}", foreground="red")
            messagebox.showerror("שגיאה", f"שגיאה ביצירת משימת הפעלה מחדש:\n{message_restart}")
            return

        restart_dt = datetime.strptime(restart_time_str, "%H:%M")
        notification_dt = restart_dt - timedelta(minutes=1)
        notification_time_str = notification_dt.strftime("%H:%M")
        
        escaped_custom_message = custom_message.replace('"', '""')
        notification_command_str = f'msg.exe * "{escaped_custom_message}"'
        
        log_info(f"Creating notification task '{NOTIFICATION_TASK_NAME}' for {notification_time_str} using command: {notification_command_str}")

        command_notification = [
            "schtasks", "/create", "/tn", NOTIFICATION_TASK_NAME,
            "/tr", notification_command_str, 
            "/sc", "DAILY", "/st", notification_time_str,
            "/rl", "HIGHEST", "/it", "/f"
        ]
        success_notification, message_notification = self._run_command(command_notification)

        if not success_notification:
            log_error(f"Failed to create notification task: {message_notification}. Deleting main task for consistency.")
            self.status_label.config(text=f"שגיאה ביצירת משימת התראה להפעלה מחדש:\n{message_notification}", foreground="red")
            messagebox.showerror("שגיאה", f"שגיאה ביצירת משימת התראה:\n{message_notification}\n\nמשימת ההפעלה מחדש נוצרה, אך ההתראה לא. מוחק את משימת ההפעלה מחדש.")
            self.delete_task(TASK_NAME)
            return

        log_info("Restart tasks created successfully.")
        self.status_label.config(text=f"הפעלה מחדש נקבעה ל-{restart_time_str} מדי יום.\nהתראה עם ההודעה המותאמת תוצג דקה לפני.", foreground="green")
        messagebox.showinfo("הצלחה", f"הפעלה מחדש נקבעה ל-{restart_time_str} מדי יום.\nהתראה עם ההודעה המותאמת תוצג ב-{notification_time_str}.")

    def cancel_restart_task(self):
        # This function content remains the same
        log_info("Attempting to cancel scheduled restart tasks.")
        self.status_label.config(text="מבטל משימות הפעלה מחדש...", foreground="orange")
        self.master.update_idletasks()

        success_main, msg_main = self.delete_task(TASK_NAME)
        success_notif, msg_notif = self.delete_task(NOTIFICATION_TASK_NAME)

        errors = []
        if not success_main and "not found" not in msg_main.lower() and "לא נמצאה" not in msg_main.lower():
            errors.append(f"שגיאה בביטול משימת הפעלה מחדש:\n{msg_main}")
        if not success_notif and "not found" not in msg_notif.lower() and "לא נמצאה" not in msg_notif.lower():
            errors.append(f"שגיאה בביטול משימת התראה:\n{msg_notif}")
            
        if errors:
            full_error_msg = "\n\n".join(errors)
            log_error(f"Errors occurred during restart task cancellation: {full_error_msg}")
            self.status_label.config(text=full_error_msg, foreground="red")
            messagebox.showerror("שגיאה", full_error_msg)
        else:
            log_info("Restart tasks cancelled successfully (or were not found).")
            self.status_label.config(text="משימות ההפעלה מחדש וההתראה בוטלו.", foreground="blue")
            messagebox.showinfo("בוטל", "משימות ההפעלה מחדש וההתראה בוטלו.")
        
        self.check_existing_restart_task()

    def check_existing_restart_task(self):
        # This function content remains the same
        log_info("Checking for existing restart task.")
        command_query_main = ["schtasks", "/query", "/tn", TASK_NAME, "/fo", "LIST"]
        success_main, output_main = self._run_command(command_query_main)

        current_status_text = self.status_label.cget("text")
        status_is_lockout_related = "נעילה" in current_status_text or "הוחלו" in current_status_text or "בוטלה" in current_status_text


        if success_main and TASK_NAME in output_main:
            log_info(f"Restart task '{TASK_NAME}' found.")
            try:
                lines = output_main.splitlines()
                task_time_str = None
                for line in lines:
                    if line.startswith("Next Run Time:") or line.startswith("זמן ריצה הבא:"):
                        time_part = line.split()[-1] 
                        task_time_str = ":".join(time_part.split(":")[:2])
                        break
                
                if task_time_str:
                    datetime.strptime(task_time_str, "%H:%M") 
                    log_info(f"Parsed existing restart task time: {task_time_str}")
                    new_status = f"משימת הפעלה מחדש קיימת לשעה {task_time_str}"
                    if status_is_lockout_related:
                        self.status_label.config(text=f"{current_status_text}\n{new_status}", foreground="green")
                    else:
                        self.status_label.config(text=new_status, foreground="green")

                    h, m = task_time_str.split(":")
                    self.hour_var.set(h)
                    self.minute_var.set(m)
                else: 
                    log_warning("Restart task found, but couldn't parse 'Next Run Time'.")
                    new_status = "משימת הפעלה מחדש קיימת (לא ניתן לקרוא שעה)."
                    if status_is_lockout_related:
                         self.status_label.config(text=f"{current_status_text}\n{new_status}", foreground="green")
                    else:
                        self.status_label.config(text=new_status, foreground="green")

            except Exception as e:
                log_exception("Error parsing existing restart task time.")
                new_status = "משימת הפעלה מחדש קיימת (שגיאה בקריאת שעה)."
                if status_is_lockout_related:
                     self.status_label.config(text=f"{current_status_text}\n{new_status}", foreground="orange")
                else:
                    self.status_label.config(text=new_status, foreground="orange")
        else: 
            log_info(f"Restart task '{TASK_NAME}' not found or error querying.")
            if not status_is_lockout_related: 
                 self.status_label.config(text="לא מוגדרת משימת הפעלה מחדש.", foreground="blue")

    def delete_task(self, task_name):
        # This function content remains the same
        log_info(f"Attempting to delete task: {task_name}")
        command = ["schtasks", "/delete", "/tn", task_name, "/f"]
        success, message = self._run_command(command)
        return success, message


# --- נקודת הכניסה הראשית ---
if __name__ == "__main__":
    if not logger: 
        messagebox.showerror("שגיאת יומן", f"לא ניתן היה ליצור את קובץ היומן {LOG_FILE_NAME}.\nאנא בדוק הרשאות בתיקייה.")
        sys.exit(1)

    if not is_admin():
        log_warning("Not running as admin. Attempting to restart.")
        print("לא רץ כמנהל. מנסה להפעיל מחדש עם הרשאות מנהל...")
        run_as_admin()
        sys.exit(0)
    else:
        log_info("--- Application Starting (Admin Mode) ---")
        root = tk.Tk()
        app = RestartSchedulerApp(root)
        try:
            root.mainloop()
            log_info("--- Application Closed ---")
        except Exception as e:
            log_exception("An unhandled error occurred in the main loop.")
            messagebox.showerror("שגיאה קריטית", f"אירעה שגיאה לא צפויה:\n{e}\n\nאנא בדוק את קובץ היומן {LOG_FILE_NAME}.")