"""
Presupuesto desde la consola.

Uso (desde la carpeta backend):
    python -m carfix ../samples/tiguan_2010.jpg --marca Volkswagen --modelo Tiguan --anio 2010
"""

import argparse
import json
from dataclasses import replace
from pathlib import Path

import cv2

from .budget import format_budget
from .config import VIDEO_EXTENSIONS, Settings
from .imaging import load_image
from .pipeline import Analyzer


def main(argv=None):
    parser = argparse.ArgumentParser(prog="carfix", description="Presupuesto de reparación a partir de una foto.")
    parser.add_argument("archivo", help="foto (o video, experimental) del vehículo")
    parser.add_argument("--marca", default="")
    parser.add_argument("--modelo", default="")
    parser.add_argument("--anio", default="")
    parser.add_argument("--part-conf", type=float, help="confianza mínima de las piezas")
    parser.add_argument("--salida", type=Path, help="carpeta de resultados (por defecto outputs/)")
    args = parser.parse_args(argv)

    settings = Settings()
    if args.part_conf is not None:
        settings = replace(settings, part_conf=args.part_conf)
    out_dir = args.salida or settings.outputs_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    analyzer = Analyzer(settings)
    vehicle = {"marca": args.marca, "modelo": args.modelo, "anio": args.anio}
    path = Path(args.archivo)

    if path.suffix.lower() in VIDEO_EXTENSIONS:
        from .video import analyze_video

        result = analyze_video(analyzer, path, vehicle,
                               progress=lambda n: print(f"\rAnalizando video... {n} cuadros", end="", flush=True))
        print()
    else:
        result = analyzer.analyze_image(load_image(path), vehicle)
        if not result.budget["vehiculo_encontrado"]:
            print("AVISO: no se encontró ningún vehículo; se analizó la foto completa.")

    print(format_budget(result.budget))

    cv2.imwrite(str(out_dir / f"{path.stem}.jpg"), result.overlay)
    (out_dir / f"{path.stem}.json").write_text(json.dumps(result.budget, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {out_dir / path.stem}.json y .jpg")
