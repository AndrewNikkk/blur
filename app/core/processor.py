import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from ultralytics import YOLO


logger = logging.getLogger(__name__)

_yolo_model = None


def get_yolo_model():
    """Ленивая инициализация yolo"""
    global _yolo_model
    if _yolo_model is None:
        model_path = Path(__file__).parent / "license_plate.pt"
        if model_path.exists():
            logger.info(f"Загрузка модели из: {model_path}")
            _yolo_model = YOLO(str(model_path))
        else:
            logger.info("Кастомная модель не найдена, используем yolov8n.pt")
            _yolo_model = YOLO("yolov8n.pt")
    return _yolo_model


def detect_object_yolo(image: np.ndarray, confidence_threshold: float = 0.5):
    try:
        model = get_yolo_model()
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = model.predict(image_rgb, conf=confidence_threshold, verbose=False)

        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x = int(x1)
                y = int(y1)
                width = int(x2 - x1)
                height = int(y2 - y1)

                padding = 5
                x = max(0, x - padding)
                y = max(0, y - padding)
                width = min(image.shape[1] - x, width + padding * 2)
                height = min(image.shape[0] - y, height + padding * 2)

                detections.append((x, y, width, height))

        return detections
    except Exception as e:
        logger.error(f"Ошибка при детекции объектов YOLO: {str(e)}")
        return []


def apply_yolo_blur(image: np.ndarray, blur_strength: int = 25, confidence_threshold: float = 0.25) -> np.ndarray:
    blurred_image = image.copy()
    detections = detect_object_yolo(image, confidence_threshold)
    logger.info(f"Детектировано объектов: {len(detections)}")

    if len(detections) == 0:
        logger.warning("Объекты не детектированы! Применяем блюр ко всему изображению.")
        blurred_image = cv2.GaussianBlur(blurred_image, (blur_strength * 2 + 1, blur_strength * 2 + 1), 0)
    else:
        for x, y, w, h in detections:
            if w > 0 and h > 0:
                roi = blurred_image[y : y + h, x : x + w]
                if roi.size > 0:
                    blurred_roi = cv2.GaussianBlur(roi, (blur_strength * 2 + 1, blur_strength * 2 + 1), 0)
                    blurred_image[y : y + h, x : x + w] = blurred_roi
        logger.info(f"Блюр применен к {len(detections)} областям")

    return blurred_image


def process_image_with_yolo(image_bytes: bytes) -> Optional[bytes]:
    """Обрабатывает изображение, применяя блюр к детектированным объектам"""
    try:
        # Конвертируем байты в numpy массив
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            logger.error("Не удалось декодировать изображение")
            return None

        logger.info(f"Размер изображения: {image.shape}")

        # Применяем блюр
        blurred_image = apply_yolo_blur(image, blur_strength=25, confidence_threshold=0.25)

        # Определяем формат по содержимому
        is_jpeg = image_bytes[:3] == b"\xff\xd8\xff" or image_bytes[:2] == b"\xff\xd8"

        if is_jpeg:
            _, buffer = cv2.imencode(".jpg", blurred_image)
        else:
            _, buffer = cv2.imencode(".png", blurred_image)

        logger.info(f"Обработанное изображение, размер: {len(buffer.tobytes())} байт")
        return buffer.tobytes()

    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {str(e)}", exc_info=True)
        return None
