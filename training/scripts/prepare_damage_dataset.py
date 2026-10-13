import json
import random
import shutil
import hashlib
from pathlib import Path
from PIL import Image

from paths import DAMAGES_DATASET, RAW_DAMAGES

SOURCE_DIR = RAW_DAMAGES

OUTPUT_DIR = DAMAGES_DATASET
SEED = 42

CLASSES = [
    "Missing part",
    "Broken part",
    "Scratch",
    "Cracked",
    "Dent",
    "Flaking",
    "Paint chip",
    "Corrosion",
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def main():
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(
            f"No existe la carpeta: {SOURCE_DIR.resolve()}\n"
            "Corregí SOURCE_DIR en el script."
        )

    # Buscar imágenes y anotaciones recursivamente.
    # Las anotaciones se llaman "<imagen con extensión>.json"
    # (ej: "Car damages 101.png.json"), así que se indexa por
    # nombre completo. Se ignoran las máscaras (masks_human,
    # masks_machine), que repiten el nombre de la imagen.
    images_by_name = {}

    for path in SOURCE_DIR.rglob("*"):
        if path.parent.name.lower().startswith("masks"):
            continue
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            images_by_name.setdefault(path.name, []).append(path)

    annotations = []

    for json_path in SOURCE_DIR.rglob("*.json"):
        # Ignorar metadatos generales.
        if json_path.name.lower() in {"meta.json", "classes.json"}:
            continue

        try:
            data = json.loads(
                json_path.read_text(encoding="utf-8-sig")
            )
        except (json.JSONDecodeError, OSError):
            continue

        objects = data.get("objects", [])
        if not objects:
            continue

        # Intentar encontrar la imagen con el mismo nombre.
        candidates = images_by_name.get(json_path.stem, [])

        # Preferir la imagen del mismo grupo (File1/ann -> File1/img).
        same_folder = [
            p for p in candidates
            if p.parent.parent == json_path.parent.parent
        ]

        if same_folder:
            image_path = same_folder[0]
        elif len(candidates) == 1:
            image_path = candidates[0]
        else:
            # No elegir arbitrariamente si hay nombres duplicados.
            continue

        annotations.append((image_path, json_path, objects))

    if not annotations:
        raise RuntimeError(
            "No se encontraron pares imagen/anotación. "
            "Revisá la estructura de carpetas del dataset."
        )

    rng = random.Random(SEED)
    rng.shuffle(annotations)

    n = len(annotations)
    n_train = int(n * 0.70)
    n_val = int(n * 0.20)

    splits = {
        "train": annotations[:n_train],
        "val": annotations[n_train:n_train + n_val],
        "test": annotations[n_train + n_val:],
    }

    class_to_id = {
        name: i for i, name in enumerate(CLASSES)
    }

    for split, items in splits.items():
        for subdir in ("images", "labels"):
            (OUTPUT_DIR / split / subdir).mkdir(
                parents=True, exist_ok=True
            )

        for image_path, json_path, objects in items:
            try:
                with Image.open(image_path) as image:
                    width, height = image.size
                    image.verify()

                # Nombre único aunque existan archivos repetidos.
                unique = hashlib.md5(
                    str(image_path.resolve()).encode()
                ).hexdigest()[:12]
                filename = f"{image_path.stem}_{unique}"

                shutil.copy2(
                    image_path,
                    OUTPUT_DIR / split / "images" /
                    f"{filename}{image_path.suffix.lower()}"
                )

                lines = []

                for obj in objects:
                    class_name = obj.get("classTitle")
                    geometry = obj.get("geometryType", "").lower()

                    if class_name not in class_to_id:
                        continue

                    if geometry != "polygon":
                        continue

                    points = obj.get("points", {}).get(
                        "exterior", []
                    )

                    if len(points) < 3:
                        continue

                    normalized = []

                    for point in points:
                        x, y = point[0], point[1]
                        x = min(max(float(x) / width, 0), 1)
                        y = min(max(float(y) / height, 0), 1)
                        normalized.extend([x, y])

                    if len(normalized) < 6:
                        continue

                    coords = " ".join(
                        f"{value:.6f}" for value in normalized
                    )
                    lines.append(
                        f"{class_to_id[class_name]} {coords}"
                    )

                label_path = (
                    OUTPUT_DIR / split / "labels" /
                    f"{filename}.txt"
                )
                label_path.write_text(
                    "\n".join(lines),
                    encoding="utf-8"
                )

            except Exception as error:
                print(f"Error con {image_path}: {error}")

        print(f"{split}: {len(items)} imágenes")

    yaml_content = (
        f"path: {OUTPUT_DIR.resolve().as_posix()}\n"
        "train: train/images\n"
        "val: val/images\n"
        "test: test/images\n\n"
        f"nc: {len(CLASSES)}\n"
        f"names: {json.dumps(CLASSES, ensure_ascii=False)}\n"
    )

    (OUTPUT_DIR / "data.yaml").write_text(
        yaml_content, encoding="utf-8"
    )

    print("\nDataset preparado en:", OUTPUT_DIR.resolve())
    print("Clases:", CLASSES)


if __name__ == "__main__":
    main()
