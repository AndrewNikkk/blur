# import os
# from pathlib import Path
from typing import Optional

from app.core.storage import get_file_path, save_processed_file


def process_file(file_path: str) -> Optional[str]:
    """
    Обрабатывает файл.
    Здесь должна быть логика обработки.
    Пока возвращает копию файла.
    """
    input_path = get_file_path(file_path)
    if not input_path or not input_path.exists():
        return None

    # Читаем оригинальный файл
    with open(input_path, "rb") as f:
        file_content = f.read()

    # Пока просто копируем
    processed_content = file_content

    # Сохраняем обработанный файл
    original_filename = input_path.name
    processed_path = save_processed_file(processed_content, original_filename)

    return processed_path
