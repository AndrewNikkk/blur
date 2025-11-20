import uuid
from pathlib import Path
from typing import Optional, Tuple


BASE_DIR = Path(__file__).parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = BASE_DIR / "processed"

# Создаем директории при импорте
UPLOADS_DIR.mkdir(exist_ok=True, parents=True)
PROCESSED_DIR.mkdir(exist_ok=True, parents=True)


def save_uploaded_file(file_content: bytes, original_filename: Optional[str]) -> Tuple[str, str]:
    """Сохраняет загруженный файл и возвращает (filename, file_path)"""
    if not original_filename:
        original_filename = "unknown_file"

    file_extension = Path(original_filename).suffix
    if not file_extension:
        file_extension = ""

    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOADS_DIR / filename

    with open(file_path, "wb") as f:
        f.write(file_content)

    return filename, str(file_path)


def save_processed_file(file_content: bytes, original_filename: str) -> str:
    """Сохраняет обработанный файл и возвращает file_path"""
    if not original_filename:
        original_filename = "unknown_file"

    file_extension = Path(original_filename).suffix
    if not file_extension:
        file_extension = ""

    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = PROCESSED_DIR / filename

    with open(file_path, "wb") as f:
        f.write(file_content)

    return str(file_path)


def get_file_path(file_path: str) -> Optional[Path]:
    """Возвращает Path к файлу, если он существует"""
    path = Path(file_path)
    if path.exists():
        return path
    return None


def delete_file(file_path: str) -> bool:
    """Удаляет файл по пути"""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except Exception:
        return False
