import cv2
import numpy as np
import os
import base64
import asyncio


class QRFinding:
    def __init__(self, photo_path: str, output_dir: str = "hasil_ekstraksi"):
        self.photo_path = photo_path
        self.output_dir = output_dir
        self.img = None
        self.results: dict[str, np.ndarray] = {}
        self.decoded_results: dict[str, str] = {}

    def load(self):
        self.img = cv2.imread(self.photo_path)

        if self.img is None:
            raise FileNotFoundError(f"Gambar tidak ditemukan: {self.photo_path}")

        return self

    async def aload(self):
        return await asyncio.to_thread(self.load)

    def process(self) -> dict[str, np.ndarray]:
        if self.img is None:
            self.load()

        B, G, R = cv2.split(self.img)

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        gray_clahe = clahe.apply(gray)

        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        _, S, _ = cv2.split(hsv)

        S_clahe = clahe.apply(S)

        extract = (
            2 * B.astype(np.int16)
            - R.astype(np.int16)
            - G.astype(np.int16)
            + 128
        )
        extract = np.clip(extract, 0, 255).astype(np.uint8)
        extract_clahe = clahe.apply(extract)

        diff = (
            2 * B.astype(np.float32)
            - R.astype(np.float32)
            - G.astype(np.float32)
        )

        extract_norm = cv2.normalize(
            diff,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        ).astype(np.uint8)

        extract_norm_clahe = clahe.apply(extract_norm)

        _, gray_otsu = cv2.threshold(
            gray_clahe,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        _, s_otsu = cv2.threshold(
            S_clahe,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        _, extract_otsu = cv2.threshold(
            extract_clahe,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        _, extract_norm_otsu = cv2.threshold(
            extract_norm_clahe,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        self.results = {
            "original": self.img,
            "gray": gray,
            "gray_clahe": gray_clahe,
            "gray_clahe_otsu": gray_otsu,

            "hsv_saturation": S,
            "hsv_saturation_clahe": S_clahe,
            "hsv_saturation_clahe_otsu": s_otsu,

            "extract_2B_R_G": extract,
            "extract_2B_R_G_clahe": extract_clahe,
            "extract_2B_R_G_clahe_otsu": extract_otsu,

            "extract_2B_R_G_norm": extract_norm,
            "extract_2B_R_G_norm_clahe": extract_norm_clahe,
            "extract_2B_R_G_norm_clahe_otsu": extract_norm_otsu,
        }

        return self.results

    async def aprocess(self) -> dict[str, np.ndarray]:
        return await asyncio.to_thread(self.process)

    def _make_scan_variants(self, image: np.ndarray) -> list[tuple[str, np.ndarray]]:
        variants = []

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            variants.append(("bgr", image))
            variants.append(("gray", gray))
        else:
            gray = image
            variants.append(("gray", gray))

        variants.append(("invert", 255 - gray))

        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        variants.append(("blur", blur))

        _, otsu = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        variants.append(("otsu", otsu))
        variants.append(("otsu_invert", 255 - otsu))

        adaptive = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            5
        )

        variants.append(("adaptive", adaptive))
        variants.append(("adaptive_invert", 255 - adaptive))

        for scale in [2, 3, 4]:
            up = cv2.resize(
                gray,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC
            )

            variants.append((f"upscale_{scale}x", up))
            variants.append((f"upscale_{scale}x_invert", 255 - up))

            _, up_otsu = cv2.threshold(
                up,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

            variants.append((f"upscale_{scale}x_otsu", up_otsu))
            variants.append((f"upscale_{scale}x_otsu_invert", 255 - up_otsu))

        return variants

    def scan_qr(self) -> dict[str, str]:
        if not self.results:
            self.process()

        detector = cv2.QRCodeDetector()
        found: dict[str, str] = {}

        for result_name, image in self.results.items():
            variants = self._make_scan_variants(image)

            for variant_name, variant_img in variants:
                key = f"{result_name}::{variant_name}"

                try:
                    data, points, _ = detector.detectAndDecode(variant_img)

                    if data:
                        found[key] = data.strip("\ufeff")
                        continue
                except cv2.error:
                    pass

                try:
                    ok, decoded_info, points, _ = detector.detectAndDecodeMulti(variant_img)

                    if ok:
                        for item in decoded_info:
                            if item:
                                found[key] = item.strip("\ufeff")
                                break
                except cv2.error:
                    pass

        self.decoded_results = found
        return found

    async def ascan_qr(self) -> dict[str, str]:
        return await asyncio.to_thread(self.scan_qr)

    def save(self):
        if not self.results:
            self.process()

        os.makedirs(self.output_dir, exist_ok=True)

        for name, image in self.results.items():
            path = os.path.join(self.output_dir, f"{name}.png")
            cv2.imwrite(path, image)

    async def asave(self):
        return await asyncio.to_thread(self.save)

    def to_base64(self) -> dict[str, str]:
        if not self.results:
            self.process()

        b64_results: dict[str, str] = {}

        for name, image in self.results.items():
            success, buffer = cv2.imencode(".png", image)

            if success:
                b64_results[name] = base64.b64encode(buffer).decode("utf-8")

        return b64_results

    async def ato_base64(self) -> dict[str, str]:
        return await asyncio.to_thread(self.to_base64)

    def get_best_preview_base64(self) -> str | None:
        if not self.results:
            self.process()

        preferred = [
            "extract_2B_R_G_clahe",
            "extract_2B_R_G_norm_clahe",
            "hsv_saturation_clahe",
            "gray_clahe",
        ]

        for name in preferred:
            image = self.results.get(name)

            if image is not None:
                success, buffer = cv2.imencode(".png", image)

                if success:
                    return base64.b64encode(buffer).decode("utf-8")

        return None

    async def aget_best_preview_base64(self) -> str | None:
        return await asyncio.to_thread(self.get_best_preview_base64)
    

    def _resize_for_scan(self, image: np.ndarray, max_width: int = 900) -> np.ndarray:
        h, w = image.shape[:2]

        if w <= max_width:
            return image

        scale = max_width / w
        new_size = (max_width, int(h * scale))

        return cv2.resize(
            image,
            new_size,
            interpolation=cv2.INTER_AREA
        )


    def scan_qr_fast(self) -> dict[str, str]:
        """
        Scan QR versi cepat.
        Tidak mencoba semua kombinasi berat.
        Cocok untuk UI/Flet agar tidak terlalu lama.
        """
        if not self.results:
            self.process()

        detector = cv2.QRCodeDetector()
        found: dict[str, str] = {}

        priority_names = [
            "original",
            "gray",
            "gray_clahe",
            "hsv_saturation_clahe",
            "extract_2B_R_G_clahe",
            "extract_2B_R_G_norm_clahe",
        ]

        for name in priority_names:
            image = self.results.get(name)

            if image is None:
                continue

            image = self._resize_for_scan(image, max_width=900)

            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            variants = []

            variants.append(("gray", gray))
            variants.append(("invert", 255 - gray))

            _, otsu = cv2.threshold(
                gray,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

            variants.append(("otsu", otsu))
            variants.append(("otsu_invert", 255 - otsu))

            # upscale ringan saja
            up = cv2.resize(
                gray,
                None,
                fx=2,
                fy=2,
                interpolation=cv2.INTER_CUBIC
            )

            variants.append(("upscale_2x", up))
            variants.append(("upscale_2x_invert", 255 - up))

            for variant_name, variant_img in variants:
                key = f"{name}::{variant_name}"

                try:
                    data, points, _ = detector.detectAndDecode(variant_img)

                    if data:
                        found[key] = data.strip("\ufeff")
                        self.decoded_results = found
                        return found

                except cv2.error:
                    pass

        self.decoded_results = found
        return found


    async def ascan_qr_fast(self) -> dict[str, str]:
        return await asyncio.to_thread(self.scan_qr_fast)