# Convierte el dataset de daños de 8 clases (data/processed/damages) a 3 clases
# pensadas para el presupuesto, en data/processed/damages_3cls:
#   0 Rotura  = Missing part + Broken part + Cracked
#   1 Golpe   = Dent
#   2 Pintura = Scratch + Flaking + Paint chip + Corrosion
#
# No modifica el dataset original. Uso:
#   python training/scripts/remap_damage_3cls.py

from pathlib import Path
import shutil

from paths import DAMAGES_3CLS_DATASET, DAMAGES_DATASET

SOURCE_DIR = DAMAGES_DATASET
OUTPUT_DIR = DAMAGES_3CLS_DATASET

OLD_CLASSES = [
    "Missing part",
    "Broken part",
    "Scratch",
    "Cracked",
    "Dent",
    "Flaking",
    "Paint chip",
    "Corrosion",
]

NEW_CLASSES = ["Rotura", "Golpe", "Pintura"]

GROUPS = {
    "Missing part": "Rotura",
    "Broken part": "Rotura",
    "Cracked": "Rotura",
    "Dent": "Golpe",
    "Scratch": "Pintura",
    "Flaking": "Pintura",
    "Paint chip": "Pintura",
    "Corrosion": "Pintura",
}

# id viejo -> id nuevo
REMAP = {
    old_id: NEW_CLASSES.index(GROUPS[name])
    for old_id, name in enumerate(OLD_CLASSES)
}


def main():
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(f"No existe la carpeta: {SOURCE_DIR.resolve()}")

    counts = [0] * len(NEW_CLASSES)

    for split in ("train", "val", "test"):
        src_images = SOURCE_DIR / split / "images"
        src_labels = SOURCE_DIR / split / "labels"
        if not src_images.exists():
            print(f"{split}: no existe, se saltea")
            continue

        dst_images = OUTPUT_DIR / split / "images"
        dst_labels = OUTPUT_DIR / split / "labels"
        dst_images.mkdir(parents=True, exist_ok=True)
        dst_labels.mkdir(parents=True, exist_ok=True)

        n_images = 0
        for image in src_images.iterdir():
            if not image.is_file():
                continue
            shutil.copy2(image, dst_images / image.name)
            n_images += 1

            label = src_labels / f"{image.stem}.txt"
            lines = []
            if label.exists():
                for line in label.read_text(encoding="utf-8").splitlines():
                    parts = line.split()
                    if not parts:
                        continue
                    new_id = REMAP[int(parts[0])]
                    counts[new_id] += 1
                    lines.append(" ".join([str(new_id)] + parts[1:]))
            (dst_labels / f"{image.stem}.txt").write_text("\n".join(lines), encoding="utf-8")

        print(f"{split}: {n_images} imágenes")

    names = ", ".join(f'"{c}"' for c in NEW_CLASSES)
    (OUTPUT_DIR / "data.yaml").write_text(
        f"path: {OUTPUT_DIR.resolve().as_posix()}\n"
        "train: train/images\n"
        "val: val/images\n"
        "test: test/images\n\n"
        f"nc: {len(NEW_CLASSES)}\n"
        f"names: [{names}]\n",
        encoding="utf-8",
    )

    print("\nInstancias por clase nueva:")
    for name, count in zip(NEW_CLASSES, counts):
        print(f"  {name}: {count}")
    print("Dataset listo:", OUTPUT_DIR.resolve())


if __name__ == "__main__":
    main()
