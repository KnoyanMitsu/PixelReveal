from flet import Control
from flet import Icons
from colors.colors import ColorsPallets
import flet as ft


class AppBar(ft.AppBar):
    def __init__(self, action: list[Control] | None = None):
        super().__init__(
            actions= action
        )

class CardNavigation(ft.Card):
    def __init__(self, title: str,describe: str, icon: type[Icons], onclick=None):
        super().__init__(
            content=ft.Container(
                bgcolor=ft.Colors.with_opacity(0.3,"secondary"),
                content=ft.Row(
                    [
                        ft.ListTile(
                            leading=ft.Icon(icon),
                            title=ft.Text(title),
                            subtitle=ft.Text(describe)
                        ),
                        ft.Icon(ft.Icons.ARROW_FORWARD)
                    ]
                ),
                border_radius=10,
                on_click= onclick
            )
            
        )

class Card(ft.Card):
    def __init__(self, title: str,describe: str, icon: type[Icons]):
        super().__init__(
            content=ft.Container(
                bgcolor=ft.Colors.with_opacity(0.5,"primary"),
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(icon),
                            title=ft.Text(title),
                            subtitle=ft.Text(describe)
                        ),
                    ]
                ),
                border_radius=10,
            )
            
        )