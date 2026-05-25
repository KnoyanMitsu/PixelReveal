from pages.qrfind import DetailPage
import flet as ft

from pages.home import HomePage


def route_change(page):
    page.views.clear()
    page.views.append(HomePage(page))

    if page.route == "/QRFinding":
        page.views.append(DetailPage(page))

    page.update()


