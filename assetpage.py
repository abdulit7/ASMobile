
import os
os.environ["FLET_SECRET_KEY"] = "mysecret123"
import flet as ft
import mysql.connector
from mysql.connector import Error
import base64
import time

class AssetFormPage:
    def __init__(self, page: ft.Page, parent=None, local_db=None):
        if page is None:
            raise ValueError("Page object must be provided to AssetFormPage")
        self.page = page
        self.parent = parent
        self.local_db = local_db
        self.attached_images = []  # Store multiple images
        self.attached_bills = []  # Store multiple bills
        self.TEMP_DIR = os.path.join(os.getcwd(), "temp")
        os.makedirs(self.TEMP_DIR, exist_ok=True)
        print(f"Initialized TEMP_DIR: {self.TEMP_DIR}, writable: {os.access(self.TEMP_DIR, os.W_OK)}")

        self.error_popup = ft.AlertDialog(title=ft.Text("Error"), content=ft.Text(""), actions=[ft.TextButton("OK", on_click=self.close_error_popup)])
        self.success_popup = ft.AlertDialog(title=ft.Text("Success"), content=ft.Text(""), actions=[ft.TextButton("OK", on_click=self.close_success_popup)])

        self.asset_model = ft.TextField(label="Model", hint_text="Model", icon=ft.Icons.DEVICE_HUB)
        self.asset_serial_number = ft.TextField(label="Serial Number", hint_text="Enter Asset Serial Number", icon=ft.Icons.DEVICE_HUB)
        self.asset_company = ft.TextField(label="Company Name", hint_text="Enter Company Name", icon=ft.Icons.BUSINESS)
        self.asset_location = ft.TextField(label="Location", hint_text="Enter Location", icon=ft.Icons.LOCATION_ON)
        self.asset_image = ft.FilePicker(on_result=self.handle_asset_image)
        self.asset_image_button = ft.ElevatedButton("Select Image or Take Photo", icon=ft.Icons.IMAGE, on_click=lambda e: self.asset_image.pick_files(allow_multiple=True, file_type="image/*", capture=True))
        self.image_display = ft.Image(width=50, height=50, fit="contain")
        self.warning_text = ft.Text("", color="red")
        self.bill_image = ft.FilePicker(on_result=self.handle_bill_image)
        self.asset_bill_button = ft.ElevatedButton("Upload Bill or Take Photo", icon=ft.Icons.ATTACH_FILE, on_click=lambda e: self.bill_image.pick_files(allow_multiple=True, file_type="image/*", capture=True))
        self.bill_display = ft.Image(width=50, height=50, fit="contain")
        self.bill_warning_text = ft.Text("", color="red")
        self.purchase_date_button = ft.ElevatedButton("Purchase Date", icon=ft.Icons.DATE_RANGE, on_click=self.open_date_picker)
        self.purchase_date = ft.DatePicker(on_change=self.update_purchase_date)

        self.asset_status = ft.Dropdown(label="Asset Status", border=ft.InputBorder.UNDERLINE, enable_filter=True, editable=True, leading_icon=ft.Icons.SEARCH,
                                       options=[ft.dropdown.Option("Available"), ft.dropdown.Option("Deployed"), ft.dropdown.Option("Disposed/Sold")])

        self.dialog = ft.AlertDialog(modal=True, bgcolor=ft.Colors.RED_100, title=ft.Text("Add/Edit Asset"),
                                    content=ft.Container(width=400, height=600, content=ft.Column(controls=[
                                        self.asset_model, self.asset_serial_number, self.asset_company, self.asset_location,
                                        self.asset_image_button, self.image_display, self.warning_text,
                                        self.asset_bill_button, self.bill_display, self.bill_warning_text,
                                        self.purchase_date_button, self.asset_status
                                    ], spacing=15, scroll=ft.ScrollMode.AUTO), padding=20),
                                    actions=[ft.TextButton("Cancel", on_click=self.close_dialog), ft.TextButton("Save", on_click=self.save_asset)],
                                    actions_alignment=ft.MainAxisAlignment.END)

        self.page.overlay.extend([self.error_popup, self.success_popup, self.asset_image, self.bill_image, self.purchase_date, self.dialog])

    def open_dialog(self):
        self.dialog.open = True
        self.page.update()

    def handle_asset_image(self, e: ft.FilePickerResultEvent):
        self.attached_images = e.files if e.files else []
        self.asset_image_button.text = f"{len(self.attached_images)} image(s) selected."
        self.image_display.src_base64 = None
        self.warning_text.value = ""
        if self.attached_images:
            file = self.attached_images[0]  # Preview the first image
            try:
                if not self.page.web and hasattr(file, 'path'):  # Desktop/mobile mode
                    with open(file.path, "rb") as f:
                        self.attached_image_bytes = f.read()
                    self.image_display.src_base64 = base64.b64encode(self.attached_image_bytes).decode('utf-8')
                    self.warning_text.value = "Image or photo selected successfully."
                else:  # Web mode (handled via upload, but upload_url is unsupported locally)
                    self.warning_text.value = "File upload not supported in local mode. Use desktop mode for file selection."
            except Exception as ex:
                self.warning_text.value = f"Error reading file: {ex}"
            self.image_display.update()
        self.warning_text.update()
        self.page.update()

    def handle_bill_image(self, e: ft.FilePickerResultEvent):
        self.attached_bills = e.files if e.files else []
        self.asset_bill_button.text = f"{len(self.attached_bills)} bill(s) selected."
        self.bill_display.src_base64 = None
        self.bill_warning_text.value = ""
        if self.attached_bills:
            file = self.attached_bills[0]  # Preview the first bill
            try:
                if not self.page.web and hasattr(file, 'path'):  # Desktop/mobile mode
                    with open(file.path, "rb") as f:
                        self.attached_bill_bytes = f.read()
                    self.bill_display.src_base64 = base64.b64encode(self.attached_bill_bytes).decode('utf-8')
                    self.bill_warning_text.value = "Bill or photo selected successfully."
                else:  # Web mode (handled via upload, but upload_url is unsupported locally)
                    self.bill_warning_text.value = "File upload not supported in local mode. Use desktop mode for file selection."
            except Exception as ex:
                self.bill_warning_text.value = f"Error reading file: {ex}"
            self.bill_display.update()
        self.bill_warning_text.update()
        self.page.update()

    def open_date_picker(self, event):
        self.purchase_date.open = True
        self.page.update()

    def update_purchase_date(self, event):
        if event.control.value:
            self.purchase_date_button.text = f"Purchase Date: {event.control.value.strftime('%Y-%m-%d')}"
        else:
            self.purchase_date_button.text = "Purchase Date"
        self.page.update()

    def close_dialog(self, event):
        self.dialog.open = False
        self.asset_model.value = ""
        self.asset_serial_number.value = ""
        self.asset_company.value = ""
        self.asset_location.value = ""
        self.attached_images = []
        self.attached_bills = []
        self.asset_image_button.text = "Select Image or Take Photo"
        self.asset_bill_button.text = "Upload Bill or Take Photo"
        self.purchase_date_button.text = "Purchase Date"
        self.asset_status.value = "Available"
        self.image_display.src_base64 = None
        self.bill_display.src_base64 = None
        self.warning_text.value = ""
        self.bill_warning_text.value = ""
        self.close_success_popup(event)
        self.page.update()

    def close_error_popup(self, event):
        self.error_popup.open = False
        self.page.update()

    def close_success_popup(self, event):
        self.success_popup.open = False
        self.dialog.open = False
        self.asset_model.value = ""
        self.asset_serial_number.value = ""
        self.asset_company.value = ""
        self.asset_location.value = ""
        self.attached_images = []
        self.attached_bills = []
        self.asset_image_button.text = "Select Image or Take Photo"
        self.asset_bill_button.text = "Upload Bill or Take Photo"
        self.purchase_date_button.text = "Purchase Date"
        self.asset_status.value = "Available"
        self.image_display.src_base64 = None
        self.bill_display.src_base64 = None
        self.warning_text.value = ""
        self.bill_warning_text.value = ""
        if self.parent and hasattr(self.parent, 'load_assets'):
            self.parent.load_assets()
        self.page.update()

    def save_asset(self, event):
        model = self.asset_model.value
        serial_number = self.asset_serial_number.value
        company = self.asset_company.value
        location = self.asset_location.value
        status = self.asset_status.value
        purchase_date = self.purchase_date_button.text.replace("Purchase Date: ", "")

        if not all([model, serial_number, company, location, purchase_date]) or purchase_date == "Purchase Date":
            self.error_popup.content = ft.Text("All fields are required.")
            self.error_popup.open = True
            self.page.update()
            return

        cursor = self.local_db.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute("SELECT id FROM assets WHERE serial_number = ?", (serial_number,))
            existing_asset = cursor.fetchone()

            if existing_asset:
                cursor.execute("""
                    UPDATE assets 
                    SET model = ?, company = ?, location = ?, purchase_date = ?, status = ?, last_sync = ?
                    WHERE serial_number = ?
                """, (model, company, location, purchase_date, status, time.strftime("%Y-%m-%d %H:%M:%S"), serial_number))
            else:
                cursor.execute("""
                    INSERT INTO assets (model, serial_number, company, location, purchase_date, status, last_sync)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (model, serial_number, company, location, purchase_date, status, time.strftime("%Y-%m-%d %H:%M:%S")))
                asset_id = cursor.lastrowid

            if self.attached_images and hasattr(self, 'attached_image_bytes'):
                for img in self.attached_images:
                    cursor.execute("""
                        INSERT INTO asset_images (asset_id, image_name, image_data, last_sync)
                        VALUES (?, ?, ?, ?)
                    """, (asset_id, img.name, self.attached_image_bytes, time.strftime("%Y-%m-%d %H:%M:%S")))
            if self.attached_bills and hasattr(self, 'attached_bill_bytes'):
                for bill in self.attached_bills:
                    cursor.execute("""
                        INSERT INTO asset_bills (asset_id, bill_name, bill_data, last_sync)
                        VALUES (?, ?, ?, ?)
                    """, (asset_id, bill.name, self.attached_bill_bytes, time.strftime("%Y-%m-%d %H:%M:%S")))

            self.local_db.commit()
            self.success_popup.content = ft.Text("Asset saved locally!")
            self.success_popup.open = True
            self.page.update()
        except Exception as e:
            self.local_db.rollback()
            self.error_popup.content = ft.Text(f"Error saving locally: {e}")
            self.error_popup.open = True
            self.page.update()
        finally:
            cursor.close()

    def sync_with_server(self):
        db_config = {"host": "200.200.200.23", "user": "root", "password": "Pak@123", "database": "asm_sys"}
        try:
            # Test MySQL connection
            conn = mysql.connector.connect(**db_config)
            conn.close()
            print("MySQL connection test successful.")

            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            local_cursor = self.local_db.cursor()

            # Ensure MySQL tables exist (create if not)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    model TEXT,
                    serial_number TEXT UNIQUE,
                    company TEXT,
                    location TEXT,
                    purchase_date TEXT,
                    status TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asset_images (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    asset_id INT,
                    image_name TEXT,
                    image_data BLOB,
                    FOREIGN KEY (asset_id) REFERENCES assets(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asset_bills (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    asset_id INT,
                    bill_name TEXT,
                    bill_data BLOB,
                    FOREIGN KEY (asset_id) REFERENCES assets(id)
                )
            """)

            # Get unsynced local assets
            local_cursor.execute("SELECT * FROM assets WHERE last_sync IS NULL OR last_sync < (SELECT MAX(last_sync) FROM assets WHERE last_sync IS NOT NULL)")
            local_assets = local_cursor.fetchall()
            print(f"Found {len(local_assets)} unsynced assets.")

            for asset in local_assets:
                asset_id, model, serial_number, company, location, purchase_date, status, last_sync = asset
                cursor.execute("SELECT id FROM assets WHERE serial_number = %s", (serial_number,))
                existing_asset = cursor.fetchone()

                if existing_asset:
                    cursor.execute("""
                        UPDATE assets 
                        SET model = %s, company = %s, location = %s, purchase_date = %s, status = %s
                        WHERE serial_number = %s
                    """, (model, company, location, purchase_date, status, serial_number))
                else:
                    cursor.execute("""
                        INSERT INTO assets (model, serial_number, company, location, purchase_date, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (model, serial_number, company, location, purchase_date, status))
                    mysql_asset_id = cursor.lastrowid
                    print(f"Inserted new asset with ID: {mysql_asset_id}")

                # Sync images
                local_cursor.execute("SELECT * FROM asset_images WHERE asset_id = ? AND (last_sync IS NULL OR last_sync < ?)", (asset_id, time.strftime("%Y-%m-%d %H:%M:%S")))
                images = local_cursor.fetchall()
                for img in images:
                    img_id, asset_id, image_name, image_data, last_sync = img
                    cursor.execute("""
                        INSERT INTO asset_images (asset_id, image_name, image_data)
                        VALUES (%s, %s, %s)
                    """, (mysql_asset_id if not existing_asset else existing_asset[0], image_name, image_data))
                    print(f"Inserted image {image_name} for asset ID: {mysql_asset_id}")

                # Sync bills
                local_cursor.execute("SELECT * FROM asset_bills WHERE asset_id = ? AND (last_sync IS NULL OR last_sync < ?)", (asset_id, time.strftime("%Y-%m-%d %H:%M:%S")))
                bills = local_cursor.fetchall()
                for bill in bills:
                    bill_id, asset_id, bill_name, bill_data, last_sync = bill
                    cursor.execute("""
                        INSERT INTO asset_bills (asset_id, bill_name, bill_data)
                        VALUES (%s, %s, %s)
                    """, (mysql_asset_id if not existing_asset else existing_asset[0], bill_name, bill_data))
                    print(f"Inserted bill {bill_name} for asset ID: {mysql_asset_id}")

                # Update last_sync for synced records
                local_cursor.execute("UPDATE assets SET last_sync = ? WHERE id = ?", (time.strftime("%Y-%m-%d %H:%M:%S"), asset_id))
                for img in images:
                    local_cursor.execute("UPDATE asset_images SET last_sync = ? WHERE id = ?", (time.strftime("%Y-%m-%d %H:%M:%S"), img[0]))
                for bill in bills:
                    local_cursor.execute("UPDATE asset_bills SET last_sync = ? WHERE id = ?", (time.strftime("%Y-%m-%d %H:%M:%S"), bill[0]))

            conn.commit()
            self.local_db.commit()
            self.success_popup.content = ft.Text("Sync with server completed!")
            self.success_popup.open = True
            self.page.update()
        except Error as e:
            error_msg = f"Sync error: {str(e)}"
            print(error_msg)  # Log to console for debugging
            self.error_popup.content = ft.Text(error_msg)
            self.error_popup.open = True
            self.page.update()
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            if 'local_cursor' in locals():
                local_cursor.close()
