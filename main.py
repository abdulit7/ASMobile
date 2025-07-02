import flet as ft
from assetpage import AssetFormPage
import sqlite3

class MyApp(ft.Container):
    def __init__(self, page, **kwargs):
        super().__init__(**kwargs)
        self.page = page
        self.padding = 10
        self.bgcolor = ft.Colors.CYAN_100
        self.border_radius = 10

        # Initialize SQLite3 database
        self.local_db = sqlite3.connect("assets.db", check_same_thread=False)
        self.initialize_local_db()

        # Initialize AssetFormPage with camera and database
        self.add_asset_dialog = AssetFormPage(self.page, self, local_db=self.local_db)

        self.asset_button = ft.ElevatedButton(
            text="Add Asset",
            icon=ft.Icons.ADD,
            on_click=lambda e: self.add_asset_dialog.open_dialog(),
            bgcolor=ft.Colors.BLUE_500,
            color=ft.Colors.WHITE,
            width=300,
            height=50
        )

        self.component_button = ft.ElevatedButton(
            text="Add Component",
            icon=ft.Icons.BUILD,
            on_click=lambda e: self.add_asset_dialog.open_dialog(),
            bgcolor=ft.Colors.GREEN_500,
            color=ft.Colors.WHITE,
            width=300,
            height=50
        )

        self.device_button = ft.ElevatedButton(
            text="Add Device",
            icon=ft.Icons.DEVICE_HUB,
            on_click=lambda e: self.add_asset_dialog.open_dialog(),
            bgcolor=ft.Colors.RED_500,
            color=ft.Colors.WHITE,
            width=300,
            height=50
        )

        self.consumable_button = ft.ElevatedButton(
            text="Add Consumable",
            icon=ft.Icons.SHOPPING_BAG,
            on_click=lambda e: self.add_asset_dialog.open_dialog(),
            bgcolor=ft.Colors.ORANGE_500,
            color=ft.Colors.WHITE,
            width=300,
            height=50
        )

        self.sync_button = ft.ElevatedButton(
            text="Sync with Server",
            icon=ft.Icons.SYNC,
            on_click=self.sync_with_server,
            bgcolor=ft.Colors.PURPLE_500,
            color=ft.Colors.WHITE,
            width=300,
            height=50
        )

        self.content = ft.Column(
            controls=[
                ft.Text("IT ASSET MANAGER", size=18, weight="bold", text_align=ft.TextAlign.CENTER),
                self.asset_button,
                self.component_button,
                self.device_button,
                self.consumable_button,
                self.sync_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

    def initialize_local_db(self):
        cursor = self.local_db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT,
                serial_number TEXT UNIQUE,
                company TEXT,
                location TEXT,
                purchase_date TEXT,
                status TEXT,
                last_sync TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asset_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER,
                image_name TEXT,
                image_data BLOB,
                last_sync TEXT,
                FOREIGN KEY (asset_id) REFERENCES assets (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asset_bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER,
                bill_name TEXT,
                bill_data BLOB,
                last_sync TEXT,
                FOREIGN KEY (asset_id) REFERENCES assets (id)
            )
        """)
        self.local_db.commit()

    def sync_with_server(self, e):
        try:
            self.add_asset_dialog.sync_with_server()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Sync with server completed!"),
                bgcolor=ft.Colors.GREEN_600
            )
            self.page.snack_bar.open = True
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Sync error: {ex}"),
                bgcolor=ft.Colors.RED_600
            )
            self.page.snack_bar.open = True
        self.page.update()

def main(page: ft.Page):
    page.title = "IT Asset Manager"
    page.window.width = 320
    page.window.height = 600
    page.theme_mode = ft.ThemeMode.LIGHT

    app = MyApp(page)
    page.add(app)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
