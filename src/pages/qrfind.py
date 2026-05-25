import flet as ft
from components.components import AppBar, Card
from colors.colors import ColorsPallets
from controller.QRFinding import QRFinding


def DetailPage(page: ft.Page):
    progress_bar = ft.ProgressBar(visible=False)
    status_text = ft.Text("")
    result_text = ft.Text("")
    image_result = ft.Image(
        src="",
        visible=False,
        width=500,
    )

    file_picker = ft.FilePicker()

    async def pick_photo_quick(e):
        photo = await file_picker.pick_files(
            dialog_title="Pilih Foto",
            allowed_extensions=["png", "jpg", "jpeg"],
            allow_multiple=False,
        )

        if not photo or not photo[0] or not photo[0].path:
            return

        progress_bar.visible = True
        image_result.visible = False
        result_text.value = ""
        page.update()

        try:
            qr = QRFinding(photo[0].path)

            await qr.aprocess()
            page.update()

            preview_b64 = await qr.aget_best_preview_base64()

            if preview_b64:
                image_result.src = preview_b64
                image_result.visible = True
            page.update()

            # pakai fast scan, bukan scan_qr penuh
            hasil_scan = await qr.ascan_qr_fast()

            if hasil_scan:
                isi = list(hasil_scan.values())[0]
                result_text.value = f"QR Found: {isi}"
            else:
                result_text.value = "QR not detect"

        except Exception as ex:
            status_text.value = "Somthing error on side, Please Make issue on github"
            result_text.value = str(ex)

        finally:
            progress_bar.visible = False
            page.update()

    async def pick_photo_deep(e):
        photo = await file_picker.pick_files(
            dialog_title="Pilih Foto",
            allowed_extensions=["png", "jpg", "jpeg"],
            allow_multiple=False,
        )

        if not photo or not photo[0] or not photo[0].path:
            return

        progress_bar.visible = True
        image_result.visible = False
        result_text.value = ""
        page.update()

        try:
            qr = QRFinding(photo[0].path)

            await qr.aprocess()
            page.update()

            preview_b64 = await qr.aget_best_preview_base64()

            if preview_b64:
                image_result.src = preview_b64
                image_result.visible = True
            page.update()

            # pakai fast scan, bukan scan_qr penuh
            hasil_scan = await qr.ascan_qr()

            if hasil_scan:
                isi = list(hasil_scan.values())[0]
                result_text.value = f"QR Found: {isi}"
            else:
                result_text.value = "QR not detect"

        except Exception as ex:
            status_text.value = "Somthing error on side, Please Make issue on github"
            result_text.value = str(ex)

        finally:
            progress_bar.visible = False
            page.update()

    return ft.View(
        route="/QRFinding",
        appbar=AppBar(),
        controls=[
            progress_bar,
            status_text,
            Card(
                "How this Work?",
                "This feature to manipulation your photo/art using Methode Channel Saturation / HVS-S and Extraction 2B-R-G + CLAHE thanks Flet to work python on Flutter",
                ft.Icons.INFO_OUTLINE,
            ),
            Card(
                "Pro tips: For Arists QR for Watermark",
                "Place QR on your Art/Photo and blend to Overlay. I Recommended you place on bright color to easy detect QR your watermark",
                ft.Icons.LIGHTBULB_CIRCLE_OUTLINED,
            ),
            Card(
                "For penimpa",
                "Dont use watermark QR and hidden QR just for Hoax or timpa teks",
                ft.Icons.WARNING_OUTLINED,
            ),
            ft.Button("Pick Photo Quick-Scan (Best for mobile)", on_click=pick_photo_quick),
            ft.Button("Pick Photo Deep-Scan (Accurate Find QR but slow)", on_click=pick_photo_deep),
            image_result,
            result_text,
        ],
        scroll=ft.ScrollMode.AUTO,
    )