"""Модуль для сегментации изображений.

Содержит функции для:
- Преобразования изображений
- Бинаризации изображений
- Обработки и кодировки/декодировки изображений
"""

import cv2
import numpy as np


def segment_image(image_bytes: bytes) -> bytes:
    """Выполняет сегментацию изображения.

    Args:
        image_bytes: Байтовое представление исходного изображения

    Returns:
        bytes: Байтовое представление сегментированного изображения

    Raises:
        ValueError: Если произошла ошибка при обработке изображения
    """
    try:
        # Конвертируем bytes в numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Пример простой сегментации (замените на вашу реальную логику)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, segmented = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # Конвертируем обратно в bytes
        _, img_encoded = cv2.imencode('.jpg', segmented)
        return img_encoded.tobytes()

    except Exception as error:
        raise ValueError(f"Segmentation error: {str(error)}") from error
