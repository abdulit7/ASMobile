import flet as ft
from assetpage import AssetFormPage

class MyApp(ft.Container):
    def __init__(self, page, **kwargs):  # Accept page as a parameter
        super().__init__(**kwargs)
        
        self.page = page  # Store the page object
        self.padding = 20
        self.bgcolor = ft.Colors.CYAN_100
        self.border_radius = 10

        self.add_asset_dialog = AssetFormPage(self.page, self)  # Pass the page object

        self.asset_button = ft.ElevatedButton(
            text="Add Asset",
            on_click=lambda e: self.add_asset_dialog.open_dialog(),
            bgcolor=ft.Colors.BLUE_500,
            color=ft.Colors.WHITE,
            width=320,
            height=50
        )

        self.component_button = ft.ElevatedButton(
            text="Add Component",
            #on_click=self.on_button_click,
            bgcolor=ft.Colors.GREEN_500,
            color=ft.Colors.WHITE,
            width=320,
            height=50
        )

        self.device_button = ft.ElevatedButton(
            text="Add Device",
            #on_click=self.on_button_click,
            bgcolor=ft.Colors.RED_500,
            color=ft.Colors.WHITE,
            width=320,
            height=50
        )
        self.consumable_button = ft.ElevatedButton(
            text="Add Consumable",
            #on_click=self.on_button_click,
            bgcolor=ft.Colors.ORANGE_500,
            color=ft.Colors.WHITE,
            width=320,
            height=50
        )

        self.content = ft.Column(
            controls=[
                ft.Text("IT ASSET MANAGER", size=18, weight="bold"),
                self.asset_button,
                self.component_button,
                self.device_button,
                self.consumable_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )


def main(page: ft.Page):
    page.title = "My Flet App"
    page.window.width = 350
    page.window.height = 600
    page.add(MyApp(page))  # Pass the page object to MyApp
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
