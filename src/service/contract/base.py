import io
import base64
import os
import random
from uuid import uuid4
import qrcode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from weasyprint import HTML
from src.service import BasicCrud
from sharq_models.models import Contract , StudyInfo #type:ignore
from src.core.config import settings
from fastapi.templating import Jinja2Templates
import jinja2

templates = Jinja2Templates(directory="src/templates")

class ContractBase(BasicCrud):
    BASE_UPLOAD_DIR = "uploads/contracts"
    CONTRACT_CONFIG = {
        "two_side": {
            "directory": "two_side",
            "template": "ikki_new.html",
            "is_three": False,
        },
        "three_side": {
            "directory": "three_side",
            "template": "uchtomon_new.html",
            "is_three": True,
        }
    }
    def __init__(self, db: AsyncSession):
        self.db = db
        self.qr_code_dir_path = self.path_builder("qr_codes", ".png")
    
    def path_builder(self, base_dir: str, extension: str) -> str:
        filename = f"{uuid4().hex}{extension}"
        return f"{self.BASE_UPLOAD_DIR}/{base_dir}/{filename}"
    
    def url_builder(self, path: str) -> str:
        return f"{settings.base_url}/{path}"

    async def _get_contract(self, user_id: int) -> Contract:
        stmt = (
            select(Contract)
            .where(Contract.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        contract = result.scalars().first()
        return contract
    
    def _get_full_name(self, passport) -> str:
        return " ".join(filter(None, [passport.last_name, passport.first_name, passport.third_name]))

    def _generate_contract_id(self) -> str:
        return str(random.randint(0, 999999)).zfill(6)
    
    def _generate_qr_code(self, contract_file_path: str) -> str:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(contract_file_path)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_str = base64.b64encode(buf.getvalue()).decode("ascii")
        return img_str
    
    def _render_contract_html(self, template_name: str, context: dict) -> jinja2.Template:
        context["qr_code"] = self._generate_qr_code(context["contract_file_path"])
        return templates.get_template(template_name).render(context)

    def _save_contract_pdf(self, html_content: str, file_path: str) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            HTML(string=html_content, base_url=".").write_pdf(f)    
            
    async def _update_in_study_info(self, user_id: int):
        # is_approved is a computed field based on contract existence
        # No need to update it in the database as it's computed dynamically
        pass
        
