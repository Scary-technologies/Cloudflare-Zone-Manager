import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import threading
import json

# خواندن توکن از فایل
with open("token.txt", "r") as file:
    CLOUDFLARE_API_TOKEN = file.read().strip()

zones_cache = []
dns_records_cache = {}
backup_records = {}

def get_zone_details(zone_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            settings = {item['id']: item['value'] for item in data['result']}
            return settings
    return {}

def get_zones_list():
    url = "https://api.cloudflare.com/client/v4/zones"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            zones = []
            for zone in data['result']:
                zone_details = get_zone_details(zone['id'])
                zones.append((
                    zone['id'], 
                    zone['name'], 
                    zone['plan']['name'], 
                    zone_details.get('security_level', 'N/A'), 
                    'Enabled' if zone_details.get('development_mode', 0) else 'Disabled', 
                    zone_details.get('ssl', 'N/A'),
                    zone_details.get('cache_level', 'N/A')
                ))
            return zones
        else:
            return []
    else:
        return []

def get_dns_records(zone_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            records = [(record['id'], record['name'], record['type'], record['content'], record['proxied']) for record in data['result']]
            dns_records_cache[zone_id] = records
            return records
        else:
            return []
    else:
        return []

def update_dns_record(zone_id, record_id, record_type, record_name, new_ip):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": record_type,
        "name": record_name,
        "content": new_ip,
        "ttl": 120,
        "proxied": False
    }
    response = requests.put(url, headers=headers, json=payload)
    return response.status_code == 200

def backup_dns_records():
    global backup_records
    backup_records = {}
    for zone_id, zone_name, plan, under_attack, dev_mode, ssl_status, cache_level in zones_cache:
        records = get_dns_records(zone_id)
        backup_records[zone_id] = records

def save_backup():
    backup_dns_records()
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, "w") as file:
            json.dump(backup_records, file)
        messagebox.showinfo("Success", "Backup saved successfully")

def load_backup():
    global backup_records
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, "r") as file:
            backup_records = json.load(file)
        restore_dns_records()
        refresh_zones()
        messagebox.showinfo("Success", "Backup restored successfully")

def restore_dns_records():
    for zone_id, records in backup_records.items():
        for record_id, record_name, record_type, record_content, record_proxied in records:
            update_dns_record(zone_id, record_id, record_type, record_name, record_content)
    refresh_zones()

def apply_new_ip():
    new_ip = ip_entry.get()
    selected_record_type = record_type_var.get()
    if not new_ip:
        messagebox.showerror("Error", "Please enter a valid IP address")
        return

    selected_zones = zone_tree.selection()
    selected_records = dns_tree.selection()

    if not selected_zones or not selected_records:
        messagebox.showerror("Error", "Please select both a zone and at least one DNS record")
        return

    # Backup current records before applying changes
    backup_dns_records()

    success = True

    for zone_item in selected_zones:
        zone_id = zone_tree.item(zone_item)['values'][0]
        for record_item in selected_records:
            record_id = dns_tree.item(record_item)['values'][0]
            record_type, record_name, record_content, record_proxied = [dns_tree.item(record_item)['values'][i] for i in range(1, 5)]
            if record_type == selected_record_type:
                if not update_dns_record(zone_id, record_id, record_type, record_name, new_ip):
                    success = False

    if success:
        messagebox.showinfo("Success", "All selected records updated successfully")
    else:
        messagebox.showerror("Error", "Failed to update some records")

    update_dns_records(None)

def enable_under_attack_mode(zone_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"value": "under_attack"}
    response = requests.patch(url, headers=headers, json=payload)
    return response.status_code == 200

def disable_under_attack_mode(zone_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"value": "medium"}
    response = requests.patch(url, headers=headers, json=payload)
    return response.status_code == 200

def toggle_under_attack_mode(enable):
    selected_zones = zone_tree.selection()

    if not selected_zones:
        messagebox.showerror("Error", "Please select at least one zone")
        return

    success = True

    for zone_item in selected_zones:
        zone_id = zone_tree.item(zone_item)['values'][0]
        if enable:
            if not enable_under_attack_mode(zone_id):
                success = False
        else:
            if not disable_under_attack_mode(zone_id):
                success = False

    if success:
        messagebox.showinfo("Success", f"Under Attack Mode {'enabled' if enable else 'disabled'} successfully for selected zones")
    else:
        messagebox.showerror("Error", f"Failed to {'enable' if enable else 'disable'} Under Attack Mode for some zones")

def enable_proxy(zone_id, record_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    record = next((rec for rec in dns_records_cache[zone_id] if rec[0] == record_id), None)
    if not record:
        return False
    record_type, record_name, record_content = record[2], record[1], record[3]
    payload = {
        "type": record_type,
        "name": record_name,
        "content": record_content,
        "ttl": 120,
        "proxied": True
    }
    response = requests.put(url, headers=headers, json=payload)
    return response.status_code == 200

def disable_proxy(zone_id, record_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    record = next((rec for rec in dns_records_cache[zone_id] if rec[0] == record_id), None)
    if not record:
        return False
    record_type, record_name, record_content = record[2], record[1], record[3]
    payload = {
        "type": record_type,
        "name": record_name,
        "content": record_content,
        "ttl": 120,
        "proxied": False
    }
    response = requests.put(url, headers=headers, json=payload)
    return response.status_code == 200

def toggle_proxy_status(enable):
    selected_zones = zone_tree.selection()
    selected_records = dns_tree.selection()

    if not selected_zones or not selected_records:
        messagebox.showerror("Error", "Please select both a zone and at least one DNS record")
        return

    success = True

    for zone_item in selected_zones:
        zone_id = zone_tree.item(zone_item)['values'][0]
        for record_item in selected_records:
            record_id = dns_tree.item(record_item)['values'][0]
            if enable:
                if not enable_proxy(zone_id, record_id):
                    success = False
            else:
                if not disable_proxy(zone_id, record_id):
                    success = False

    if success:
        messagebox.showinfo("Success", f"Proxy {'enabled' if enable else 'disabled'} successfully")
    else:
        messagebox.showerror("Error", f"Failed to {'enable' if enable else 'disable'} proxy for some records")

    update_dns_records(None)

def refresh_zones():
    global zones_cache
    zones_cache = get_zones_list()
    for i in zone_tree.get_children():
        zone_tree.delete(i)
    for zone_id, zone_name, plan, under_attack, dev_mode, ssl_status, cache_level in zones_cache:
        zone_tree.insert("", "end", values=(zone_id, zone_name, plan, under_attack, dev_mode, ssl_status, cache_level))

def update_dns_records(event):
    selected_items = zone_tree.selection()
    if not selected_items:
        return

    selected_item = selected_items[0]
    zone_id = zone_tree.item(selected_item)['values'][0]
    records = get_dns_records(zone_id)
    for i in dns_tree.get_children():
        dns_tree.delete(i)
    for record in records:
        if len(record) == 5:
            record_id, record_name, record_type, record_content, record_proxied = record
            dns_tree.insert("", "end", values=(record_id, record_name, record_type, record_content, "Yes" if record_proxied else "No"))

def cache_data():
    global zones_cache
    zones_cache = get_zones_list()
    for zone_id, zone_name, plan, under_attack, dev_mode, ssl_status, cache_level in zones_cache:
        get_dns_records(zone_id)
    root.after(0, refresh_zones)

def start_cache_thread():
    cache_thread = threading.Thread(target=cache_data)
    cache_thread.start()

# ایجاد رابط کاربری
root = tk.Tk()
root.title("Cloudflare DNS Manager")
root.geometry("1000x700")

header = tk.Label(root, text="Cloudflare DNS Manager", font=("Arial", 24))
header.pack(pady=10)

description = tk.Label(root, text="Manage your DNS records easily with backup and restore functionality.", font=("Arial", 12, "italic"))
description.pack(pady=5)

ip_frame = tk.Frame(root)
ip_frame.pack(pady=10)
ip_label = tk.Label(ip_frame, text="New IP Address:", font=("Arial", 12))
ip_label.pack(side=tk.LEFT)
ip_entry = tk.Entry(ip_frame, font=("Arial", 12))
ip_entry.pack(side=tk.LEFT, padx=5)

record_type_var = tk.StringVar(value="A")
record_type_dropdown = ttk.Combobox(ip_frame, textvariable=record_type_var, values=["A", "AAAA", "CNAME", "MX", "TXT"], font=("Arial", 12))
record_type_dropdown.pack(side=tk.LEFT, padx=5)

apply_button = tk.Button(ip_frame, text="Apply New IP to All Records", command=apply_new_ip, font=("Arial", 12))
apply_button.pack(side=tk.LEFT, padx=5)

restore_button = tk.Button(ip_frame, text="Restore Records from Backup", command=load_backup, font=("Arial", 12))
restore_button.pack(side=tk.LEFT, padx=5)

backup_button = tk.Button(ip_frame, text="Save Backup to File", command=save_backup, font=("Arial", 12))
backup_button.pack(side=tk.LEFT, padx=5)

under_attack_frame = tk.Frame(root)
under_attack_frame.pack(pady=10)

enable_under_attack_button = tk.Button(under_attack_frame, text="Enable Under Attack Mode", command=lambda: toggle_under_attack_mode(True), font=("Arial", 12))
enable_under_attack_button.pack(side=tk.LEFT, padx=5)

disable_under_attack_button = tk.Button(under_attack_frame, text="Disable Under Attack Mode", command=lambda: toggle_under_attack_mode(False), font=("Arial", 12))
disable_under_attack_button.pack(side=tk.LEFT, padx=5)

proxy_frame = tk.Frame(root)
proxy_frame.pack(pady=10)

enable_proxy_button = tk.Button(proxy_frame, text="Enable Proxy", command=lambda: toggle_proxy_status(True), font=("Arial", 12))
enable_proxy_button.pack(side=tk.LEFT, padx=5)

disable_proxy_button = tk.Button(proxy_frame, text="Disable Proxy", command=lambda: toggle_proxy_status(False), font=("Arial", 12))
disable_proxy_button.pack(side=tk.LEFT, padx=5)

zone_frame = tk.Frame(root)
zone_frame.pack(pady=10, fill=tk.BOTH, expand=True)
zone_tree = ttk.Treeview(zone_frame, columns=("Zone ID", "Zone Name", "Plan", "Under Attack", "Dev Mode", "SSL Status", "Cache Level"), show="headings", selectmode="extended")
zone_tree.heading("Zone ID", text="Zone ID")
zone_tree.heading("Zone Name", text="Zone Name")
zone_tree.heading("Plan", text="Plan")
zone_tree.heading("Under Attack", text="Under Attack")
zone_tree.heading("Dev Mode", text="Dev Mode")
zone_tree.heading("SSL Status", text="SSL Status")
zone_tree.heading("Cache Level", text="Cache Level")
zone_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
zone_tree.bind("<<TreeviewSelect>>", update_dns_records)

dns_frame = tk.Frame(root)
dns_frame.pack(pady=10, fill=tk.BOTH, expand=True)
dns_tree = ttk.Treeview(dns_frame, columns=("ID", "Name", "Type", "Content", "Proxied"), show="headings", selectmode="extended")
dns_tree.heading("ID", text="ID")
dns_tree.heading("Name", text="Name")
dns_tree.heading("Type", text="Type")
dns_tree.heading("Content", text="Content")
dns_tree.heading("Proxied", text="Proxied")
dns_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

refresh_button = tk.Button(root, text="Refresh Zones", command=start_cache_thread, font=("Arial", 12))
refresh_button.pack(pady=10)

# شروع کش داده‌ها
start_cache_thread()
root.mainloop()
