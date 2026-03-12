# CobaltRedAlertDesktop

מערכת זו בודקת את אתר פיקוד העורף, ואם מתקבלת התראה רלוונטית לאזורים שנבחרו - מופיע על המסך פופ אפ עם פרטי ההתראה, ומנוגן קובץ שמע של אזעקה עולה ויורדת.

זוהי גרסת הדסקטופ, שלא שולחת התראות בSMS או במייל.
אם ברצונך לקבל התראות בSMS או במייל, ראה את הפרוייקט השני שלנו.
https://github.com/shilosiani/CobaltRedAlert

---

## דרישות מערכת

יש לוודא ש־Python 3.7 ומעלה מותקן.

### התקנת תלויות:

```bash
pip install -r requirements.txt
```


---

## קבצים עיקריים

| קובץ | תיאור |
|------|--------|
| `RedAlertDesktop.py` | התוכנה |
| `alert.mp3` | צליל האזעקה |
| `Alerts.json` | מבנה קובץ ההתראות של פיקוד העורף |
| `RedAlert.py` | הקובץ שסורק את שרתי פקע"ר ומציג התראות במקרה הצורך |

---

## שימוש

### בחירת איזורי התראה:

הרץ את RedAlertDesktop.py ובחר איזורי התראה,
לאחר מכן לחץ על הפעל.


## קריאות לשרת פקע"ר


הסקריפט רץ בלולאה תמידית ובודק התראות כל שניה. ניתן לשנות זאת ע"י עריכת השורה:
```python
time.sleep(1)
```
כדי שלא תתקבל התראה זהה פעמיים, עשינו שאחרי שהוא מזהה התראה יחכה 100 שניות (כאמור, לא בקובץ הזה), כי ההתראות הכי ארוכות ממה שבדקנו נשארות בקובץ הנ"ל דקה וחצי ורצינו לקחת קצת מרווח ביטחון.

אם אתם רוצים לדמות התראות לצורך בדיקות, העלו את קובץ Alerts.json לשרת שלכם והזינו בסקריפט את הקישור אליו. הוא באותו המבנה כמו זה של פיקוד העורף.

---

---

## פיתוח ותרומה

תרגישו חופשי להציע שיפורים, לדווח על באגים או להוסיף תכונות חדשות.

אהבתם את התוכנה? אפשר לתרום לי כאן
https://ko-fi.com/ashivered

---

## רישיונות צד שלישי


צליל הסירנה בתוכנה ניתן באדיבות היוצר Delilah, תחת רישיון [Creative Commons Attribution 3.0](https://creativecommons.org/licenses/by/3.0/).  
שם הקובץ: "Tornado Siren II"  
מקור: [https://soundbible.com/1937-Tornado-Siren-II.html](https://soundbible.com/1937-Tornado-Siren-II.html)  

---

The siren sound used in this software is by Delilah, licensed under the [Creative Commons Attribution 3.0](https://creativecommons.org/licenses/by/3.0/) license.  
File name: "Tornado Siren II"  
Source: [https://soundbible.com/1937-Tornado-Siren-II.html](https://soundbible.com/1937-Tornado-Siren-II.html)  


