import requests
import flet as ft
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

# تنظیمات لاگ‌گذاری
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelیهs)s - %(message)s')

# متغیرهای سراسری
API_TOKEN = ''
BASE_URL = 'https://api.cloudflare.com/client/v4/'
headers = {}
request_times = []
zone_ids_map = {}
zones = []

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
                return []
        logging.info(f"Total {len(zones)} zones retrieved")
        return zones
    except requests.exceptions.RequestException as e:
        logging.exception("An error occurred while retrieving zones")
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
        logging.exception("An error occurred while retrieving security level for zone ID {zone_id}")
        return "Unknown"

def set_security_level(zone_ids, level, page):
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
                page.dialog.open = True
                page.update()
        except requests.exceptions.RequestException as e:
            logging.exception(f"An error occurred while setting security level for zone ID {zone_id}")
    update_list(page)

def update_list(page, filter_text=''):
    global zone_ids_map, zones
    logging.info("Updating the list of zones")
    zone_ids_map = {}
    zones_list.controls.clear()  # پاک کردن لیست قبل از اضافه کردن نتایج جدید

    if not zones:
        zones = get_zones()

    if zones:
        def update_zones():
            filtered_zones = [zone for zone in zones if filter_text.lower() in zone["name"].lower()]
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_zone = {executor.submit(get_security_level, zone["id"]): zone for zone in filtered_zones}
                for future in as_completed(future_to_zone):
                    zone = future_to_zone[future]
                    try:
                        security_level = future.result()
                        zone_item = ft.Row([ft.Checkbox(label=zone["name"], value=False, on_change=on_checkbox_change), ft.Text(security_level)])
                        zone_ids_map[zone_item.controls[0]] = zone["id"]
                        zones_list.controls.append(zone_item)
                    except Exception as e:
                        logging.exception(f"An error occurred while processing zone ID {zone['id']}")
            page.update()
            logging.info("List update complete")

        threading.Thread(target=update_zones).start()

def on_checkbox_change(e):
    pass  # می‌توانید هر عملی که لازم است را اینجا اضافه کنید

def main(page: ft.Page):
    global zones_list, API_TOKEN, headers
    page.title = "Cloudflare Zone Manager"
    page.scroll = "adaptive"
    page.padding = 20
    page.window_width=600
    page.window_height=600

    def on_set_under_attack(e):
        selected_items = [zone_ids_map[item.controls[0]] for item in zones_list.controls if isinstance(item.controls[0], ft.Checkbox) and item.controls[0].value]
        threading.Thread(target=set_security_level, args=(selected_items, 'under_attack', page)).start()

    def on_set_default_security(e):
        selected_items = [zone_ids_map[item.controls[0]] for item in zones_list.controls if isinstance(item.controls[0], ft.Checkbox) and item.controls[0].value]
        threading.Thread(target=set_security_level, args=(selected_items, 'medium', page)).start()

    def on_token_submit(e):
        global API_TOKEN, headers
        API_TOKEN = token_input.value
        headers = {
            'Authorization': f'Bearer {API_TOKEN}',
            'Content-Type': 'application/json',
        }
        page.dialog.open = False
        page.update()
        update_list(page)  # بارگیری لیست پس از وارد کردن توکن

    def on_filter_change(e):
        update_list(page, filter_text=filter_input.value)

    # Dialog برای ورود توکن
    token_input = ft.TextField(label="API Token", password=True, multiline=False, width=400)
    token_submit_button = ft.ElevatedButton(text="Submit", on_click=on_token_submit)
    token_dialog = ft.AlertDialog(
        title=ft.Text("Enter your Cloudflare API Token"),
        content=ft.Column([token_input, token_submit_button], alignment="center"),
        open=True,
        modal=True,
    )

    page.dialog = token_dialog

    update_button = ft.ElevatedButton(text="Update List", on_click=lambda e: update_list(page))
    under_attack_button = ft.ElevatedButton(text="Set Under Attack", on_click=on_set_under_attack)
    default_security_button = ft.ElevatedButton(text="Set Default Security", on_click=on_set_default_security)
    filter_input = ft.TextField(label="Filter Domains", on_change=on_filter_change, width=600)

    zones_list = ft.Column()  # لیستی برای نگه‌داری مناطق

    # استفاده از یک Container برای نگه‌داری دکمه‌ها
    button_container = ft.Container(

    content=ft.Row([update_button, under_attack_button, default_security_button], alignment="spaceBetween"),
    margin=20,
    padding=10,
    bgcolor=ft.colors.SURFACE_VARIANT,
    border_radius=10,
    shadow=ft.BoxShadow(blur_radius=10, spread_radius=5, color=ft.colors.BLACK45))
    # اضافه کردن کامپوننت‌ها به صفحه
    page.add(ft.Column([filter_input, zones_list,button_container]))
    page.dialog = token_dialog
    page.update()
#PR-M:)
ft.app(target=main)
