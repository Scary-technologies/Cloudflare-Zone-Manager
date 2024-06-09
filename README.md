### Overview of Cloudflare DNS Manager

The Cloudflare DNS Manager is a graphical user interface (GUI) application developed using Python and the Tkinter library. It allows users to manage their DNS records and various Cloudflare settings easily. The application leverages the Cloudflare API to interact with Cloudflare's DNS services and provides features such as backup and restore of DNS records, toggling the "Under Attack Mode", and managing proxy status.

#### Key Features

1. **DNS Record Management**:
   - View DNS records for multiple zones.
   - Update IP addresses for DNS records.
   - Toggle the proxy status for individual DNS records.
   - Support for various DNS record types (A, AAAA, CNAME, MX, TXT).

2. **Zone Management**:
   - View a list of all zones associated with the Cloudflare account.
   - Display detailed information about each zone, including plan type, SSL status, cache level, and whether development mode is enabled.
   - Toggle "Under Attack Mode" for one or more zones.

3. **Backup and Restore**:
   - Backup DNS records to a JSON file.
   - Restore DNS records from a backup file, allowing for easy recovery and management of DNS settings.

#### User Interface

The user interface is designed with ease of use in mind, providing a clear layout for managing DNS records and Cloudflare settings. The main components include:

- **Header and Description**:
  - A header displaying the application name.
  - A brief description of the application’s functionality.

- **IP Management Frame**:
  - An input field for entering a new IP address.
  - A dropdown menu to select the DNS record type.
  - Buttons to apply the new IP to all selected records, restore records from backup, and save backups to a file.

- **Zone and DNS Record Tables**:
  - A tree view for displaying zone information, including zone ID, zone name, plan, under attack status, development mode, SSL status, and cache level.
  - A tree view for displaying DNS records, including record ID, name, type, content, and proxy status.

- **Action Buttons**:
  - Buttons to enable or disable "Under Attack Mode".
  - Buttons to enable or disable the proxy for selected DNS records.
  - A refresh button to update the zone list.

#### How to Use

1. **Initialization**:
   - Ensure the `token.txt` file contains your Cloudflare API token.

2. **Viewing and Managing Zones**:
   - The application will automatically fetch and display the list of zones upon startup.
   - Select a zone from the list to view its DNS records.

3. **Updating DNS Records**:
   - Enter a new IP address and select the DNS record type.
   - Click "Apply New IP to All Records" to update the IP for all selected records of the specified type.

4. **Backup and Restore**:
   - Click "Save Backup to File" to backup current DNS records to a JSON file.
   - Click "Restore Records from Backup" to load DNS records from a backup file.

5. **Toggling "Under Attack Mode"**:
   - Select one or more zones.
   - Click "Enable Under Attack Mode" or "Disable Under Attack Mode" to toggle the status.

6. **Managing Proxy Status**:
   - Select one or more DNS records.
   - Click "Enable Proxy" or "Disable Proxy" to toggle the proxy status for the selected records.

The Cloudflare DNS Manager simplifies DNS management tasks and provides a robust set of tools for managing and securing your domains through the Cloudflare API.
