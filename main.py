import flet as ft
from assetpage import AssetFormPage
import sqlite3

class MyApp(ft.Container):
    def __init__(self, page, **kwargs):
        super().__init__(**kwargs)
        self.page = page
        self.padding = 0  # Remove padding from container to control it within layout

        # Initialize SQLite3 database
        self.local_db = sqlite3.connect("assets.db", check_same_thread=False)
        self.initialize_local_db()

        # Initialize AssetFormPage with camera and database
        self.add_asset_dialog = AssetFormPage(self.page, self, local_db=self.local_db)

        # Buttons
        self.asset_button = ft.ElevatedButton(
            text="Add Asset",
            icon=ft.Icons.ADD,
            on_click=lambda e: self.add_asset_dialog.open_dialog(),
            bgcolor=ft.Colors.BLUE_500,
            color=ft.Colors.WHITE,
            width=280,
            height=50
        )

        self.component_button = ft.ElevatedButton(
            text="Add Component",
            icon=ft.Icons.BUILD,
            on_click=lambda e: self.add_asset_dialog.open_dialog(),
            bgcolor=ft.Colors.GREEN_500,
            color=ft.Colors.WHITE,
            width=280,
            height=50
        )

        self.device_button = ft.ElevatedButton(
            text="Add Device",
            icon=ft.Icons.DEVICE_HUB,
            on_click=lambda e: self.add_asset_dialog.open_dialog(),
            bgcolor=ft.Colors.RED_500,
            color=ft.Colors.WHITE,
            width=280,
            height=50
        )

        self.consumable_button = ft.ElevatedButton(
            text="Add Consumable",
            icon=ft.Icons.SHOPPING_BAG,
            on_click=lambda e: self.add_asset_dialog.open_dialog(),
            bgcolor=ft.Colors.ORANGE_500,
            color=ft.Colors.WHITE,
            width=280,
            height=50
        )

        self.sync_button = ft.ElevatedButton(
            text="Sync with Server",
            icon=ft.Icons.SYNC,
            on_click=self.sync_with_server,
            bgcolor=ft.Colors.PURPLE_500,
            color=ft.Colors.WHITE,
            width=280,
            height=50
        )

        # Content Area with Border
        self.content_area = ft.Container(
            content=ft.Column(
                controls=[
                    self.asset_button,
                    self.component_button,
                    self.device_button,
                    self.consumable_button,
                    self.sync_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            padding=10,
            bgcolor=ft.Colors.WHITE,
            width=300,
            height=420,  # Adjusted height to fit within 600px with AppBar (60px) and BottomAppBar (80px)
        )

        # Main Layout
        self.content = ft.Column(
            controls=[
                self.content_area,
            ],
            expand=True,
            spacing=0,
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

    # Top AppBar
    page.appbar = ft.AppBar(
        title=ft.Text("IT ASSET MANAGER", size=18, weight="bold"),
        bgcolor=ft.Colors.GREEN_300,
        color=ft.Colors.WHITE,
        center_title=True,
        automatically_imply_leading=False,
    )

    # Floating Action Button
    page.floating_action_button = ft.FloatingActionButton(
        content=ft.Icon(ft.Icons.ADD, color=ft.Colors.BLUE_500),
        bgcolor=ft.Colors.WHITE,
        shape=ft.CircleBorder(),
        on_click=lambda e: page.add_asset_dialog.open_dialog() if hasattr(page, 'add_asset_dialog') else None,
    )
    page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED

    # BottomAppBar with Menu Options in Menu Button
    page.bottom_appbar = ft.BottomAppBar(
        bgcolor=ft.Colors.BLUE,
        shape=ft.NotchShape.CIRCULAR,
        content=ft.Row(
            controls=[
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(text="Option 1"),
                        ft.PopupMenuItem(text="Option 2"),
                        ft.PopupMenuItem(text="Option 3"),
                        ft.PopupMenuItem(text="Option 4"),
                    ],
                    icon=ft.Icon(ft.Icons.MENU_BOOK, color=ft.Colors.WHITE),
                    tooltip="Menu Options",
                ),
                ft.IconButton(icon=ft.Icons.SEARCH, icon_color=ft.Colors.WHITE, tooltip="Search"),
                ft.Container(expand=True),  # Spacer to push "More" menu to the right
                # ft.PopupMenuButton(
                #     items=[
                #         ft.PopupMenuItem(text="Option 1"),
                #         ft.PopupMenuItem(text="Option 2"),
                #         ft.PopupMenuItem(text="Option 3"),
                #         ft.PopupMenuItem(text="Option 4"),
                #     ],
                #     icon=ft.Icon(ft.Icons.MORE_VERT, color=ft.Colors.WHITE),
                #     tooltip="More Options",
                # ),
                ft.IconButton(icon=ft.Icons.FAVORITE, icon_color=ft.Colors.WHITE, tooltip="Favorites"),
            ],
        ),
    )

    app = MyApp(page)
    page.add(app)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
