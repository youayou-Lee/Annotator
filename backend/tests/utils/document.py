import random
import string
from typing import Optional

from sqlalchemy.orm import Session

from app.models.document import Document
from tests.utils.utils import random_lower_string

def create_random_document(db: Session, owner_id: int) -> Document:
    """创建一个随机文档"""
    filename = f"{random_lower_string()}.txt"
    document = Document(
        filename=filename,
        original_filename=filename,
        file_path=f"/tmp/{filename}",
        file_size=random.randint(100, 1000),
        file_type=".txt",
        uploader_id=owner_id
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document 