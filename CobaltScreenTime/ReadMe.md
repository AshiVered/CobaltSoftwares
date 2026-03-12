
# CobaltScreenTime

**CobaltScreenTime** is a Windows utility for managing and restricting computer usage time.  

---

## ✨ Features

- ⏰ **Login Restriction by Time Range**  
  Prevents login to a specific user account during defined hours.  
  > Users already logged in will **not be forcibly logged out**.

- 🔁 **Scheduled Automatic Restart**  
  Restarts the computer daily at a specified time, useful for enforcing logout during restricted periods.

- 💬 **Optional Warning Message**  
  Displays a custom message before the scheduled restart, giving the user time to save their work.

---


## 🧩 Usage Example

To block user access from **01:00 AM to 06:00 AM**, and ensure they are logged out:

1. Set login restriction for the desired user between `01:00`–`06:00`.
2. Set a scheduled reboot at `01:00`.
3. (Optional) Enable a warning message to be displayed at `00:59`.

> ⚠️ The login restriction **only blocks new logins** — it doesn't affect users already signed in.  
> To enforce logout, combine it with the reboot feature.

---

## 🔐 Important Notes

- Be careful when applying login restrictions to **administrator accounts**.  
  If blocked, you won’t be able to log in — even with the correct password.

- After a reboot, the login restriction applies immediately based on the configured schedule.

- Use responsibly. This tool is intended for **local** time-management enforcement and is not a security feature.

---

## 📁 License

This project is licensed under the GNU GPL V3 License. See [LICENSE](LICENSE) for details.

---

