### Overview (English)

#### Cloudflare Zone Manager

Cloudflare Zone Manager is a Python-based application designed to manage Cloudflare zones efficiently. This repository provides two implementations: one using the Flet framework and another using Tkinter for the graphical user interface (GUI).

#### Features

- **Retrieve Zones**: Fetch all zones from your Cloudflare account.
- **Dynamic Timeout**: Adjust request timeout dynamically based on average response times.
- **Security Level Management**: View and update the security levels of your zones.
- **Multi-threaded Requests**: Uses concurrent requests to improve performance.
- **User-friendly Interface**: Choose between Flet and Tkinter for the GUI.

#### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Scary-technologies/Cloudflare-Zone-Manager.git
    cd Cloudflare-Zone-Manager
    ```

2. **Install the required packages:**

    For Flet UI:
    ```bash
    pip install -r requirements-Flet-UI.txt
    ```

    For Tkinter UI:
    ```bash
    pip install -r requirements-tkinter.txt
    ```

#### Usage

1. **Run the application:**

    For Flet UI:
    ```bash
    python Main-With-Flet.py
    ```

    For Tkinter UI:
    ```bash
    python Main-With-tkinter.py
    ```

2. **Enter your Cloudflare API Token in the dialog box that appears.**

3. **Use the interface to:**
    - Update the list of zones.
    - Set security levels to "Under Attack" or default security.

#### Code Overview

- **Logging**: Configured to display detailed debug information and errors.
- **API Interaction**: Functions for retrieving zones and updating security levels using Cloudflare API.
- **Dynamic Timeout**: Calculates optimal timeout based on past request times.
- **Multi-threading**: Improves performance by handling multiple requests concurrently.
- **GUI Options**: Provides a modern, interactive GUI using either Flet or Tkinter.

#### Contributing

Contributions are welcome! Please open an issue or submit a pull request with your improvements.

#### License

This project is licensed under the MIT License. See the LICENSE file for details.

### Overview (فارسی)

#### Cloudflare Zone Manager

Cloudflare Zone Manager یک برنامه مبتنی بر پایتون است که برای مدیریت ناحیه‌های Cloudflare طراحی شده است. این مخزن دو پیاده‌سازی ارائه می‌دهد: یکی با استفاده از فریمورک Flet و دیگری با استفاده از Tkinter برای رابط کاربری گرافیکی (GUI).

#### ویژگی‌ها

- **بازیابی ناحیه‌ها**: تمام ناحیه‌های حساب Cloudflare شما را بازیابی می‌کند.
- **زمان‌بندی دینامیک**: زمان انتظار درخواست‌ها را بر اساس میانگین زمان‌های پاسخ تنظیم می‌کند.
- **مدیریت سطح امنیتی**: مشاهده و به‌روزرسانی سطوح امنیتی ناحیه‌های شما.
- **درخواست‌های چند رشته‌ای**: از درخواست‌های موازی برای بهبود عملکرد استفاده می‌کند.
- **رابط کاربری کاربر پسند**: انتخاب بین Flet و Tkinter برای GUI.

#### نصب

1. **کلون کردن مخزن:**

    ```bash
    git clone https://github.com/Scary-technologies/Cloudflare-Zone-Manager.git
    cd Cloudflare-Zone-Manager
    ```

2. **نصب بسته‌های مورد نیاز:**

    برای رابط کاربری Flet:
    ```bash
    pip install -r requirements-Flet-UI.txt
    ```

    برای رابط کاربری Tkinter:
    ```bash
    pip install -r requirements-tkinter.txt
    ```

#### استفاده

1. **اجرای برنامه:**

    برای رابط کاربری Flet:
    ```bash
    python Main-With-Flet.py
    ```

    برای رابط کاربری Tkinter:
    ```bash
    python Main-With-tkinter.py
    ```

2. **توکن API Cloudflare خود را در جعبه دیالوگ که ظاهر می‌شود وارد کنید.**

3. **استفاده از رابط کاربری برای:**
    - به‌روزرسانی لیست ناحیه‌ها.
    - تنظیم سطوح امنیتی به "Under Attack" یا امنیت پیش‌فرض.

#### نمای کلی کد

- **لاگ‌گذاری**: پیکربندی شده برای نمایش اطلاعات دقیق و خطاها.
- **تعامل با API**: توابع برای بازیابی ناحیه‌ها و به‌روزرسانی سطوح امنیتی با استفاده از API Cloudflare.
- **زمان‌بندی دینامیک**: محاسبه زمان انتظار بهینه بر اساس زمان‌های درخواست گذشته.
- **چند رشته‌ای**: بهبود عملکرد با مدیریت چندین درخواست به صورت همزمان.
- **گزینه‌های GUI**: ارائه یک رابط کاربری مدرن و تعاملی با استفاده از Flet یا Tkinter.

#### مشارکت

مشارکت‌ها استقبال می‌شود! لطفاً یک issue باز کنید یا یک pull request با بهبودهای خود ارسال کنید.
