
from router.router import route_change
import flet as ft
from colors.colors import ColorsPallets


def main(page: ft.Page):
    page.theme = ft.Theme(color_scheme= ft.ColorScheme(
        primary= ColorsPallets.PRIMARY,
        secondary= ColorsPallets.SECONDARY
    ),
    use_material3= True
    )
    page.dark_theme = ft.Theme(color_scheme= ft.ColorScheme(
        primary= ColorsPallets.PRIMARY_DARK,
        secondary= ColorsPallets.SECONDARY_DARK
    ),
    use_material3= True
    )
    page.title = "Flet App"

    async def view_pop(e):
        if e.view is not None:
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = lambda e: route_change(page)
    page.on_view_pop = view_pop

    route_change(page)

ft.run(main) 