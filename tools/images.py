from typing import Tuple, Literal

from PIL import Image, ImageDraw, ImageOps

Position = Literal[
    "top-left",
    "top-right",
    "bottom-left",
    "bottom-right",
]


class ImageTool:
    WATERMARK_BRIGHTNESS_THRESHOLD = 180

    def __init__(self, image: Image.Image):
        self.image = image

    @staticmethod
    def _get_average_brightness(image: Image.Image) -> float:
        pixel = image.convert("RGB").resize((1, 1), Image.Resampling.BILINEAR).getpixel(
            (0, 0)
        )
        red, green, blue = pixel

        return (red * 0.299) + (green * 0.587) + (blue * 0.114)

    @staticmethod
    def _invert_logo_colors(logo: Image.Image) -> Image.Image:
        red, green, blue, alpha = logo.split()
        inverted = ImageOps.invert(Image.merge("RGB", (red, green, blue))).convert("RGBA")
        inverted.putalpha(alpha)

        return inverted

    def stick_watermark(
        self,
        logo: Image.Image,
        margin: Tuple[int, int],
        position: Position = "top-right",
        logo_width: int | None = None,
    ) -> Image.Image:
        image = self.image.convert("RGBA")
        logo = logo.convert("RGBA")

        # Resize Logo While Keeping Aspect Ratio
        if logo_width is not None:
            ratio = logo_width / logo.width
            logo_height = int(logo.height * ratio)

            logo = logo.resize(
                (logo_width, logo_height),
                Image.Resampling.LANCZOS,
            )

        margin_x, margin_y = margin

        # Calculate Logo Position
        if position == "top-left":
            x = margin_x
            y = margin_y

        elif position == "top-right":
            x = image.width - logo.width - margin_x
            y = margin_y

        elif position == "bottom-left":
            x = margin_x
            y = image.height - logo.height - margin_y

        elif position == "bottom-right":
            x = image.width - logo.width - margin_x
            y = image.height - logo.height - margin_y

        else:
            raise ValueError(f"Unsupported Position: {position}")

        target_area = image.crop((x, y, x + logo.width, y + logo.height))
        brightness = self._get_average_brightness(target_area)
        if brightness >= self.WATERMARK_BRIGHTNESS_THRESHOLD:
            # Users usually upload a white watermark, so invert it on bright backgrounds for contrast.
            logo = self._invert_logo_colors(logo)

        # Paste Logo With Transparency
        image.paste(logo, (x, y), logo)

        return image

    def add_smart_border(
        self,
        border_px: int,
    ) -> Image.Image:
        image = self.image.convert("RGB")

        # Resize For Faster Analysis
        small_image = image.resize((100, 100))

        # Quantize To Find Dominant Color
        palette_image = small_image.quantize(colors=5)

        # Get Dominant Color
        palette = palette_image.getpalette()
        color_counts = sorted(
            palette_image.getcolors(),
            reverse=True,
        )

        dominant_color_index = color_counts[0][1]

        dominant_color = tuple(
            palette[dominant_color_index * 3 : dominant_color_index * 3 + 3]
        )

        bordered_image = image.copy()
        draw = ImageDraw.Draw(bordered_image)
        border_px = min(border_px, image.width // 2, image.height // 2)

        # Draw Filled Border Inside The Existing Image
        draw.rectangle((0, 0, image.width, border_px), fill=dominant_color)
        draw.rectangle(
            (0, image.height - border_px, image.width, image.height),
            fill=dominant_color,
        )
        draw.rectangle((0, 0, border_px, image.height), fill=dominant_color)
        draw.rectangle(
            (image.width - border_px, 0, image.width, image.height),
            fill=dominant_color,
        )

        return bordered_image
