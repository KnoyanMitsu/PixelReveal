import flet as ft
from components.components import AppBar, CardNavigation,Card
from colors.colors import ColorsPallets

def HomePage(page: ft.Page):
    async def open_detail():
        await page.push_route("/QRFinding")

    return ft.View(
        route="/",
        appbar=AppBar(action=[ft.IconButton(ft.Icons.INFO_ROUNDED)]),
        controls=[
            Card("Information","This App using Flet of course very beta. if you notice or look of bugs tell me.", ft.Icons.INFO_OUTLINE),
            ft.ListView([
                CardNavigation("Finding QR", "Finding QR with manipulation on photo", ft.Icons.QR_CODE, onclick=open_detail),
            ])
        ]
    )
