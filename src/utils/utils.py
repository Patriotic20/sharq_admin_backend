import os
from uuid import uuid4
import qrcode
import random

def generate_file_path(base_dir: str, extension: str) -> str:
        filename = f"{uuid4().hex}{extension}"
        full_path = os.path.join(base_dir, filename)
        os.makedirs(base_dir, exist_ok=True)
        return full_path


def generate_qr_code(data: str, save_path: str) -> None:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save(save_path)


def generate_contract_id(length: int = 6) -> str:
    return ''.join(random.choices('0123456789', k=length))
