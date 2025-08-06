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


def number_to_uzbek(n):
    ones = ["", "bir", "ikki", "uch", "to'rt", "besh", "olti", "yetti", "sakkiz", "to'qqiz"]
    tens = ["", "o'n", "yigirma", "o'ttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "to'qson"]
    hundreds = ["", "bir yuz", "ikki yuz", "uch yuz", "to'rt yuz", "besh yuz", "olti yuz", "yetti yuz", "sakkiz yuz", "to'qqiz yuz"]
    

    if n == 0:
        return "nol"
    
    result = []

    # Handle billions
    if n >= 1000000000:
        billions = n // 1000000000
        if billions == 1:
            result.append("bir milliard")
        else:
            result.append(number_to_uzbek(billions) + " milliard")
        n %= 1000000000

    # Handle millions
    if n >= 1000000:
        millions = n // 1000000
        if millions == 1:
            result.append("bir million")
        else:
            result.append(number_to_uzbek(millions) + " million")
        n %= 1000000

    # Handle thousands
    if n >= 1000:
        thousands = n // 1000
        if thousands == 1:
            result.append("bir ming")
        else:
            result.append(number_to_uzbek(thousands) + " ming")
        n %= 1000

    # Handle hundreds
    if n >= 100:
        result.append(hundreds[n // 100])
        n %= 100

    # Handle tens
    if n >= 10:
        result.append(tens[n // 10])
        n %= 10

    # Handle ones
    if n > 0:
        result.append(ones[n])
    
    return " ".join([word for word in result if word]).strip()
