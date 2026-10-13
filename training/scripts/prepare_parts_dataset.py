
from pathlib import Path
import json
import random
import shutil

from paths import PARTS_DATASET, RAW_PARTS

# ============================================================
# CONFIGURACIÓN
# ============================================================

SOURCE_DIR = RAW_PARTS

OUTPUT_DIR = PARTS_DATASET

TRAIN_RATIO = 0.70
VAL_RATIO = 0.20
TEST_RATIO = 0.10

SEED = 42

# Extensiones de imagen aceptadas
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


# ============================================================
# FUNCIONES
# ============================================================

def load_classes(meta_path):
    """Lee las clases desde meta.json."""

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    classes = meta["classes"]

    class_names = []
    class_id_by_title = {}

    for index, cls in enumerate(classes):
        title = cls["title"]

        class_names.append(title)
        class_id_by_title[title] = index

    return class_names, class_id_by_title


def find_images():
    """Busca todas las imágenes dentro de File1/img."""

    image_dir = SOURCE_DIR / "File1" / "img"

    if not image_dir.exists():
        raise FileNotFoundError(
            f"No existe la carpeta de imágenes:\n{image_dir}"
        )

    images = [
        p for p in image_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]

    return images


def polygon_to_yolo(points, image_width, image_height):
    """
    Convierte puntos [x, y] a coordenadas normalizadas YOLO.

    YOLO segmentation:
    x1 y1 x2 y2 x3 y3 ...
    """

    normalized = []

    for x, y in points:

        x_norm = max(0.0, min(1.0, x / image_width))
        y_norm = max(0.0, min(1.0, y / image_height))

        normalized.append(x_norm)
        normalized.append(y_norm)

    return normalized


def get_image_size(image_path):
    """Obtiene ancho y alto usando Pillow."""

    from PIL import Image

    with Image.open(image_path) as image:
        return image.size


def convert_annotation(image_path, annotation_path, output_label_path,
                       class_id_by_title):

    with open(annotation_path, "r", encoding="utf-8") as f:
        annotation = json.load(f)

    width, height = get_image_size(image_path)

    yolo_lines = []

    for obj in annotation.get("objects", []):

        # Solamente queremos polígonos
        if obj.get("geometryType") != "polygon":
            continue

        class_title = obj.get("classTitle")

        if class_title not in class_id_by_title:
            print(
                f"[WARNING] Clase desconocida: {class_title}"
            )
            continue

        points = obj.get("points", {}).get("exterior", [])

        if len(points) < 3:
            continue

        class_id = class_id_by_title[class_title]

        normalized_points = polygon_to_yolo(
            points,
            width,
            height
        )

        line = (
            str(class_id)
            + " "
            + " ".join(
                f"{value:.6f}"
                for value in normalized_points
            )
        )

        yolo_lines.append(line)

    output_label_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_label_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("\n".join(yolo_lines))


def create_directories():

    for split in ["train", "val", "test"]:

        (OUTPUT_DIR / "images" / split).mkdir(
            parents=True,
            exist_ok=True
        )

        (OUTPUT_DIR / "labels" / split).mkdir(
            parents=True,
            exist_ok=True
        )


def create_yaml(class_names):

    yaml_path = OUTPUT_DIR / "data.yaml"

    lines = [
        f"path: {OUTPUT_DIR.resolve()}",
        "",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "",
        "names:"
    ]

    for index, name in enumerate(class_names):
        lines.append(f"  {index}: {name}")

    with open(
        yaml_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("\n".join(lines))

    print(f"[OK] Creado: {yaml_path}")


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("AUTOMOTIVE AI - PREPARACIÓN DATASET DE PARTES")
    print("=" * 60)

    # --------------------------------------------------------
    # META
    # --------------------------------------------------------

    meta_path = SOURCE_DIR / "meta.json"

    if not meta_path.exists():
        raise FileNotFoundError(
            f"No se encontró meta.json:\n{meta_path}"
        )

    class_names, class_id_by_title = load_classes(meta_path)

    print("\nClases encontradas:")

    for index, name in enumerate(class_names):
        print(f"  {index}: {name}")

    # --------------------------------------------------------
    # IMÁGENES
    # --------------------------------------------------------

    images = find_images()

    print(f"\nImágenes encontradas: {len(images)}")

    if len(images) == 0:
        raise RuntimeError(
            "No se encontraron imágenes."
        )

    # --------------------------------------------------------
    # SHUFFLE
    # --------------------------------------------------------

    random.seed(SEED)

    random.shuffle(images)

    total = len(images)

    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    train_images = images[:train_end]
    val_images = images[train_end:val_end]
    test_images = images[val_end:]

    print("\nDivisión:")

    print(f"  Train: {len(train_images)}")
    print(f"  Val:   {len(val_images)}")
    print(f"  Test:  {len(test_images)}")

    # --------------------------------------------------------
    # DIRECTORIOS
    # --------------------------------------------------------

    create_directories()

    # --------------------------------------------------------
    # PROCESAR
    # --------------------------------------------------------

    splits = {
        "train": train_images,
        "val": val_images,
        "test": test_images
    }

    annotation_dir = SOURCE_DIR / "File1" / "ann"

    processed = 0

    for split, split_images in splits.items():

        print(f"\nProcesando {split}...")

        for image_path in split_images:

            annotation_path = annotation_dir / (
                image_path.name + ".json"
            )

            if not annotation_path.exists():

                print(
                    f"[WARNING] No existe anotación para "
                    f"{image_path.name}"
                )

                continue

            destination_image = (
                OUTPUT_DIR
                / "images"
                / split
                / image_path.name
            )

            destination_label = (
                OUTPUT_DIR
                / "labels"
                / split
                / f"{image_path.stem}.txt"
            )

            # Copiar imagen
            shutil.copy2(
                image_path,
                destination_image
            )

            # Convertir anotación
            convert_annotation(
                image_path,
                annotation_path,
                destination_label,
                class_id_by_title
            )

            processed += 1

    # --------------------------------------------------------
    # YAML
    # --------------------------------------------------------

    create_yaml(class_names)

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("PROCESO TERMINADO")
    print("=" * 60)

    print(f"\nImágenes procesadas: {processed}")

    print(
        f"\nDataset generado en:\n"
        f"{OUTPUT_DIR.resolve()}"
    )

    print("\nEstructura:")

    print("""
training/data/processed/parts/
├── data.yaml
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
""")


if __name__ == "__main__":
    main()

