import wx
import json
import subprocess
import os

# שם קובץ הקונפיגורציה
CONFIG_FILE = 'config.json'

class ConfigEditorFrame(wx.Frame):
    def __init__(self, parent, title):
        # יצירת החלון הראשי
        super(ConfigEditorFrame, self).__init__(parent, title=title, size=(550, 450))

        # יצירת פאנל שיכיל את כל הרכיבים
        self.panel = wx.Panel(self)

        # יצירת Sizer ראשי שיסדר את הרכיבים בצורה אנכית
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- כותרות ---
        font_title = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_text = wx.StaticText(self.panel, label="CobaltRedAlert")
        title_text.SetFont(font_title)
        title_text.SetForegroundColour(wx.Colour(0, 0, 0)) # צבע שחור

        font_subtitle = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        subtitle_text1 = wx.StaticText(self.panel, label="Desktop edition")
        subtitle_text1.SetFont(font_subtitle)
        subtitle_text1.SetForegroundColour(wx.Colour(0, 0, 0))

        subtitle_text2 = wx.StaticText(self.panel, label="V0.2 beta")
        subtitle_text2.SetFont(font_subtitle)
        subtitle_text2.SetForegroundColour(wx.Colour(0, 0, 0))

        # הוספת הכותרות ל-Sizer עם מרווחים ומיקום במרכז
        main_sizer.Add(title_text, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        main_sizer.Add(subtitle_text1, 0, wx.ALIGN_CENTER | wx.TOP, 5)
        main_sizer.Add(subtitle_text2, 0, wx.ALIGN_CENTER | wx.TOP, 5)
        main_sizer.AddSpacer(20)

        # --- טקסט הוראות ---
        instruction_text = wx.StaticText(self.panel, label="הכנס שמות אזורי התראה רצויים, הפרד בינהם באמצעות פסיק:")
        instruction_text.SetForegroundColour(wx.Colour(0, 0, 0))
        main_sizer.Add(instruction_text, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)

        # --- תיבת טקסט ---
        self.areas_text_ctrl = wx.TextCtrl(self.panel, style=wx.TE_RIGHT)
        self.areas_text_ctrl.SetMinSize((400, 30))
        self.areas_text_ctrl.SetBackgroundColour(wx.Colour(wx.WHITE)) # צבע כחלחל
        main_sizer.Add(self.areas_text_ctrl, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        main_sizer.AddSpacer(20)

        # --- כפתורים מרכזיים (שמור והפעל) ---
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.save_button = wx.Button(self.panel, label="שמור שינויים")
        self.run_button = wx.Button(self.panel, label="הפעל")
        
        buttons_sizer.Add(self.save_button, 0, wx.RIGHT, 10)
        buttons_sizer.Add(self.run_button, 0, wx.LEFT, 10)
        main_sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER)
        
        # --- כפתור אודות (בצד) ---
        # שימוש ב-AddStretchSpacer כדי "לדחוף" את הכפתור לתחתית החלון
        main_sizer.AddStretchSpacer(1)
        self.about_button = wx.Button(self.panel, label="אודות")
        main_sizer.Add(self.about_button, 0, wx.ALIGN_RIGHT | wx.ALL, 15)

        # קישור בין הכפתורים לפונקציות המתאימות
        self.Bind(wx.EVT_BUTTON, self.on_save, self.save_button)
        self.Bind(wx.EVT_BUTTON, self.on_run, self.run_button)
        self.Bind(wx.EVT_BUTTON, self.on_about, self.about_button)

        # טעינת הנתונים מהקובץ בפתיחת התוכנה
        self.load_config()

        # הגדרת ה-Sizer לפאנל והתאמת גודל החלון
        self.panel.SetSizer(main_sizer)
        self.Centre()
        self.Show()

    def load_config(self):
        """טוענת את רשימת האזורים מקובץ ה-JSON ומציגה אותה בתיבת הטקסט."""
        if not os.path.exists(CONFIG_FILE):
            # אם הקובץ לא קיים, משאירים את התיבה ריקה
            wx.MessageBox(f"קובץ הגדרות '{CONFIG_FILE}' לא נמצא. הוא ייווצר בשמירה הראשונה.", "אזהרה", wx.OK | wx.ICON_WARNING)
            return

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                areas = data.get("allowed_areas", [])
                # ממיר את רשימת המחרוזות למחרוזת אחת המופרדת בפסיק ורווח
                self.areas_text_ctrl.SetValue(", ".join(areas))
        except (json.JSONDecodeError, IOError) as e:
            wx.MessageBox(f"שגיאה בקריאת קובץ ההגדרות:\n{e}", "שגיאה", wx.OK | wx.ICON_ERROR)

    def on_save(self, event):
        """שומרת את הטקסט מהתיבה לקובץ ה-JSON."""
        text_content = self.areas_text_ctrl.GetValue()
        
        # ממיר את המחרוזת בחזרה לרשימה. מסיר רווחים מיותרים ומסנן ערכים ריקים
        areas_list = [area.strip() for area in text_content.split(',') if area.strip()]
        
        data_to_save = {"allowed_areas": areas_list}
        
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                # ensure_ascii=False כדי לשמור על עברית, indent=4 לעיצוב יפה של הקובץ
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            
            wx.MessageBox("השינויים נשמרו בהצלחה!", "שמירה", wx.OK | wx.ICON_INFORMATION)
        except IOError as e:
            wx.MessageBox(f"שגיאה בשמירת הקובץ:\n{e}", "שגיאה", wx.OK | wx.ICON_ERROR)

    def on_run(self, event):
        """מריצה את הסקריפט הראשי וסוגרת את החלון הנוכחי."""
        script_to_run = 'RedAlert.py'
        if not os.path.exists(script_to_run):
            wx.MessageBox(f"הקובץ '{script_to_run}' לא נמצא.\nלא ניתן להפעיל את התוכנה.", "שגיאה", wx.OK | wx.ICON_ERROR)
            return

        try:
            # הרצת הסקריפט כתהליך חדש
            subprocess.Popen(['python', script_to_run])
            self.Close()  # סגירת חלון ההגדרות
            wx.MessageBox(
                "הופעל; אין לסגור את חלון שורת הפקודה", 
                "הפעלה", 
                wx.OK | wx.ICON_INFORMATION
            )
        except Exception as e:
            wx.MessageBox(f"שגיאה בהרצת התוכנה:\n{e}", "שגיאה", wx.OK | wx.ICON_ERROR)

    def on_about(self, event):
        """מציגה חלון 'אודות'."""
        about_message = """
        CobaltRedAlert - Desktop Edition
        גרסה: V0.2 beta

        תוכנה להתראות צבע אדום.
        פותחה על ידי אשי ורד ושילה סיאני
        """
        wx.MessageBox(about_message, "אודות התוכנה", wx.OK | wx.ICON_INFORMATION)

if __name__ == '__main__':
    app = wx.App(False)
    frame = ConfigEditorFrame(None, "CobaltRedAlert - Settings")
    app.MainLoop()