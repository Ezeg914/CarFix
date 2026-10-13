# Modelos del backend

| Archivo      | Origen                                            | Qué hace |
|--------------|---------------------------------------------------|----------|
| `parts.pt`   | `training/runs/automotive_parts_v1/weights/best.pt`  | Segmenta 21 piezas |
| `damage.pt`  | `training/runs/automotive_damage_v3/weights/best.pt` | Segmenta daños: Rotura, Golpe, Pintura |
| `vehicle.pt` | `yolo11n-seg.pt` de Ultralytics (COCO)            | Encuentra el vehículo en la foto |

Para probar un modelo nuevo, copiá su `best.pt` acá con el mismo nombre
(guardá el anterior por si hay que volver).
