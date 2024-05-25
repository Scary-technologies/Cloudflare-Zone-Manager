import requests
import tkinter as tk
from tkinter import messagebox, ttk
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

# تنظیمات لاگ‌گذاری
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# تعریف توکن API و آدرس پایه API
API_TOKEN = 'توکن'  # جایگزین با توکن API خود
BASE_URL = 'https://api.cloudflare.com/client/v4/'

# هدرهای درخواست
headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json',
}

# زمان‌بندی درخواست‌ها
request_times = []

def dynamic_timeout():
    if request_times:
        avg_time = sum(request_times) / len(request_times)
        return max(10, avg_time * 2)  # حداقل زمان timeout 10 ثانیه است
    return 10

def time_request(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    request_times.append(end_time - start_time)
    if len(request_times) > 100:
        request_times.pop(0)  # حذف قدیمی‌ترین زمان‌ها برای محدود کردن لیست
    return result

def get_zones():
    logging.info("Retrieving zones from Cloudflare\n")
    try:
        zones = []
        page = 1
        while True:
            url = BASE_URL + f'zones?per_page=100&page={page}'
            response = time_request(requests.get, url, headers=headers, timeout=dynamic_timeout())
            if response.status_code == 200:
                result = response.json()['result']
                if not result:
                    break
                zones.extend(result)
                logging.debug(f"Retrieved page {page} with {len(result)} zones")
                page += 1
            else:
                logging.error(f"Failed to retrieve zones: {response.status_code} - {response.json()}")
                messagebox.showerror("Error", f"Failed to retrieve zones: {response.status_code}\n{response.json()}")
                return []
        logging.info(f"Total {len(zones)} zones retrieved")
        return zones
    except requests.exceptions.RequestException as e:
        logging.exception("An error occurred while retrieving zones")
        messagebox.showerror("Error", f"An error occurred: {e}")
        return []

def get_security_level(zone_id):
    logging.info(f"Retrieving security level for zone ID {zone_id}")
    try:
        url = BASE_URL + f'zones/{zone_id}/settings/security_level'
        response = time_request(requests.get, url, headers=headers, timeout=dynamic_timeout())
        if response.status_code == 200:
            security_level = response.json()['result']['value']
            logging.debug(f"Security level for zone ID {zone_id} is {security_level}")
            return security_level
        else:
            logging.warning(f"Failed to retrieve security level for zone ID {zone_id}: {response.status_code}")
            return "Unknown"
    except requests.exceptions.RequestException as e:
        logging.exception(f"An error occurred while retrieving security level for zone ID {zone_id}")
        return "Unknown"

def set_security_level(zone_ids, level):
    logging.info(f"Setting security level to {level} for zone IDs {zone_ids}")
    for zone_id in zone_ids:
        try:
            url = BASE_URL + f'zones/{zone_id}/settings/security_level'
            data = {
                'value': level
            }
            response = time_request(requests.patch, url, headers=headers, json=data, timeout=dynamic_timeout())
            if response.status_code == 200:
                logging.info(f"Successfully set zone {zone_id} to {level} mode")
            else:
                logging.error(f"Failed to set zone {zone_id} to {level} mode: {response.status_code} - {response.json()}")
                messagebox.showerror("Error", f"Failed to set zone {zone_id} to {level} mode: {response.status_code}\n{response.json()}")
        except requests.exceptions.RequestException as e:
            logging.exception(f"An error occurred while setting security level for zone ID {zone_id}")
            messagebox.showerror("Error", f"An error occurred: {e}")
    update_list()

def on_set_under_attack():
    selected_items = treeview.selection()
    if selected_items:
        zone_ids = [zone_ids_map[item] for item in selected_items]
        threading.Thread(target=set_security_level, args=(zone_ids, 'under_attack')).start()

def on_set_default_security():
    selected_items = treeview.selection()
    if selected_items:
        zone_ids = [zone_ids_map[item] for item in selected_items]
        threading.Thread(target=set_security_level, args=(zone_ids, 'medium')).start()  # یا هر سطح امنیتی که حالت پیش‌فرض شما باشد

def update_list():
    global zone_ids_map
    logging.info("Updating the list of zones")
    zone_ids_map = {}
    for row in treeview.get_children():
        treeview.delete(row)
    zones = get_zones()

    if zones:
        def update_zones():
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_zone = {executor.submit(get_security_level, zone["id"]): zone for zone in zones}
                for future in as_completed(future_to_zone):
                    zone = future_to_zone[future]
                    try:
                        security_level = future.result()
                        root.after(0, add_to_treeview, zone, security_level)
                    except Exception as e:
                        logging.exception(f"An error occurred while processing zone ID {zone['id']}")
            logging.info("List update complete")

        threading.Thread(target=update_zones).start()

def add_to_treeview(zone, security_level):
    item_id = treeview.insert("", "end", values=(zone["name"], security_level))
    zone_ids_map[item_id] = zone["id"]

# ایجاد پنجره اصلی
try:
    root = tk.Tk()
    root.title("Cloudflare Zone Manager")

    # تنظیم تم ttk
    style = ttk.Style(root)
    style.theme_use('clam')

    # ایجاد Frame برای قرار دادن Treeview و Scrollbar
    frame = ttk.Frame(root)
    frame.pack(expand=True, fill='both')

    # ایجاد Treeview برای نمایش سایت‌ها
    columns = ("Domain", "Security Level")
    treeview = ttk.Treeview(frame, columns=columns, show='headings', selectmode="extended")
    treeview.heading("Domain", text="Domain")
    treeview.heading("Security Level", text="Security Level")
    treeview.pack(side='left', expand=True, fill='both')

    # ایجاد اسکرول بار و اتصال آن به Treeview
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=treeview.yview)
    scrollbar.pack(side='right', fill='y')
    treeview.configure(yscroll=scrollbar.set)

    # ایجاد Frame برای قرار دادن دکمه‌ها
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)

    # ایجاد دکمه برای تغییر حالت به "Under Attack"
    btn_set_under_attack = ttk.Button(button_frame, text="Set Under Attack", command=on_set_under_attack)
    btn_set_under_attack.pack(side='left', padx=5)

    # ایجاد دکمه برای تغییر حالت به "Default Security"
    btn_set_default_security = ttk.Button(button_frame, text="Set Default Security", command=on_set_default_security)
    btn_set_default_security.pack(side='left', padx=5)

    # به‌روزرسانی لیست با اطلاعات فعلی
    threading.Thread(target=update_list).start()

    # اجرای حلقه اصلی Tkinter
    root.mainloop()
except Exception as e:
    logging.exception("An error occurred in the main loop")
    messagebox.showerror("Error", f"An error occurred: {e}")
