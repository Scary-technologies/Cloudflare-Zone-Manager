import requests
import tkinter as tk
from tkinter import messagebox, ttk
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def get_zones():
    logging.info("Retrieving zones from Cloudflare\n")
    try:
        zones = []
        page = 1
        while True:
            url = BASE_URL + f'zones?per_page=10&page={page}'
            response = requests.get(url, headers=headers)
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
    except Exception as e:
        logging.exception("An error occurred while retrieving zones")
        messagebox.showerror("Error", f"An error occurred: {e}")
        return []

def get_security_level(zone_id):
    logging.info(f"Retrieving security level for zone ID {zone_id}")
    try:
        url = BASE_URL + f'zones/{zone_id}/settings/security_level'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            security_level = response.json()['result']['value']
            logging.debug(f"Security level for zone ID {zone_id} is {security_level}")
            return security_level
        else:
            logging.warning(f"Failed to retrieve security level for zone ID {zone_id}: {response.status_code}")
            return "Unknown"
    except Exception as e:
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
            response = requests.patch(url, headers=headers, json=data)
            if response.status_code == 200:
                logging.info(f"Successfully set zone {zone_id} to {level} mode")
            else:
                logging.error(f"Failed to set zone {zone_id} to {level} mode: {response.status_code} - {response.json()}")
                messagebox.showerror("Error", f"Failed to set zone {zone_id} to {level} mode: {response.status_code}\n{response.json()}")
        except Exception as e:
            logging.exception(f"An error occurred while setting security level for zone ID {zone_id}")
            messagebox.showerror("Error", f"An error occurred: {e}")
    update_list()

def on_set_under_attack():
    selected_items = treeview.selection()
    if selected_items:
        zone_ids = [zone_ids_map[item] for item in selected_items]
        set_security_level(zone_ids, 'under_attack')

def on_set_default_security():
    selected_items = treeview.selection()
    if selected_items:
        zone_ids = [zone_ids_map[item] for item in selected_items]
        set_security_level(zone_ids, 'medium')  # یا هر سطح امنیتی که حالت پیش‌فرض شما باشد

def update_list():
    global zone_ids_map
    logging.info("Updating the list of zones")
    zone_ids_map = {}
    for row in treeview.get_children():
        treeview.delete(row)
    zones = get_zones()
    
    # اجرای درخواست‌های get_security_level به صورت موازی
    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_zone = {executor.submit(get_security_level, zone["id"]): zone for zone in zones}
        for future in as_completed(future_to_zone):
            zone = future_to_zone[future]
            try:
                security_level = future.result()
                item_id = treeview.insert("", "end", values=(zone["name"], security_level))
                zone_ids_map[item_id] = zone["id"]
            except Exception as e:
                logging.exception(f"An error occurred while processing zone ID {zone['id']}")
    
    logging.info("List update complete")

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

    # ایجاد دکمه برای تغییر حالت به "Under Attack"
    btn_set_under_attack = ttk.Button(root, text="Set Under Attack", command=on_set_under_attack)
    btn_set_under_attack.pack(pady=10)

    # ایجاد دکمه برای تغییر حالت به "Default Security"
    btn_set_default_security = ttk.Button(root, text="Set Default Security", command=on_set_default_security)
    btn_set_default_security.pack(pady=10)

    # به‌روزرسانی لیست با اطلاعات فعلی
    update_list()

    # اجرای حلقه اصلی Tkinter
    root.mainloop()
except Exception as e:
    logging.exception("An error occurred in the main loop")
    messagebox.showerror("Error", f"An error occurred: {e}")
