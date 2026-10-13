"""Decisión por pieza (cambiar / reparar / pintar) y armado del presupuesto."""

from .config import Settings

CAMBIAR, REPARAR, PINTAR, REVISAR, IGNORAR = "cambiar", "reparar", "pintar", "revisar", "ignorar"


def decide(damages, rule, settings: Settings, use_part_conf=True):
    """Devuelve (acción, motivo, [(concepto, precio)])."""
    if rule is None:
        return REVISAR, "pieza sin regla en la tabla", []
    if rule["tipo"] == "ignorar":
        return IGNORAR, "pieza que no se presupuesta", []

    nombre = rule["nombre"]
    part_conf = rule["conf_minima"] if use_part_conf else 0.0
    sure = [d for d in damages if d["conf"] >= max(settings.min_decision_conf(d["categoria"]), part_conf)]
    if not sure:
        return REVISAR, "daños de baja confianza, revisar a mano", []

    if rule["tipo"] == "cambio":
        items = [(f"Repuesto {nombre}", rule["repuesto"]),
                 (f"Mano de obra cambio {nombre}", rule["mano_obra_cambio"])]
        if rule["pintura"]:
            items.append((f"Pintura {nombre}", rule["pintura"]))
        return CAMBIAR, "pieza que se cambia ante cualquier daño", items

    def coverage(category):
        return min(sum(d["cobertura"] for d in sure if d["categoria"] == category), 1.0)

    categories = {d["categoria"] for d in sure}
    dent, broken = coverage("Golpe"), coverage("Rotura")

    # Chapa: se pinta siempre que haya daño.
    if "Rotura" in categories and broken > rule["umbral_rotura"]:
        action, reason = CAMBIAR, f"rotura ({broken:.0%} de la pieza)"
    elif "Golpe" in categories and dent > rule["umbral_cambio"]:
        action, reason = CAMBIAR, f"golpe grande ({dent:.0%} de la pieza)"
    elif "Rotura" in categories:
        action, reason = REPARAR, f"rotura chica ({broken:.0%} de la pieza)"
    elif "Golpe" in categories:
        action, reason = REPARAR, f"golpe chico ({dent:.0%} de la pieza)"
    else:
        action, reason = PINTAR, "daño superficial de pintura"

    paint = (f"Pintura {nombre}", rule["pintura"])
    if action == CAMBIAR:
        items = [(f"Repuesto {nombre}", rule["repuesto"]),
                 (f"Mano de obra cambio {nombre}", rule["mano_obra_cambio"]), paint]
    elif action == REPARAR:
        items = [(f"Reparación chapa {nombre}", rule["mano_obra_reparacion"]), paint]
    else:
        items = [paint]
    return action, reason, items


def build_budget(assigned, unassigned, rules, vehicle, settings: Settings, use_part_conf=True):
    """
    Arma el presupuesto. Las piezas en "revisar" se devuelven aparte y no suman
    al total (son detecciones dudosas, por ej. reflejos en vidrios).
    """
    lines, review = [], []
    for (key, name), damages in assigned.items():
        rule = rules.get(name)
        action, reason, items = decide(damages, rule, settings, use_part_conf)
        if action == IGNORAR:
            continue
        nombre = rule["nombre"] if rule else name
        if "#" in key:
            nombre += f" ({key.split('#')[1]})"
        line = {
            "pieza": key,
            "nombre": nombre,
            "accion": action,
            "motivo": reason,
            "danios": damages,
            "items": [{"concepto": c, "precio": p} for c, p in items],
            "subtotal": sum(p for _, p in items),
        }
        (review if action == REVISAR else lines).append(line)

    return {
        "vehiculo": vehicle,
        "piezas": lines,
        "revisar": review,
        "danios_sin_pieza": unassigned,
        "total": sum(l["subtotal"] for l in lines),
        "faltan_precios": any(not i["precio"] for l in lines for i in l["items"]),
    }


def format_budget(budget) -> str:
    """Texto legible del presupuesto, para la consola."""
    v = budget["vehiculo"]
    out = ["", "=" * 60, f"PRESUPUESTO  {v['marca']} {v['modelo']} {v['anio']}".rstrip(), "=" * 60]
    if not budget["piezas"]:
        out.append("No se detectaron daños sobre piezas.")
    for line in budget["piezas"]:
        out.append(f"\n{line['nombre']}: {line['accion'].upper()} ({line['motivo']})")
        for d in line["danios"]:
            frames = f", en {d['cuadros']} cuadros" if "cuadros" in d else ""
            out.append(f"   - {d['clase']} ({d['conf']:.0%}), cubre {d['cobertura']:.0%}{frames}")
        for item in line["items"]:
            price = f"$ {item['precio']:,.0f}" if item["precio"] else "sin precio"
            out.append(f"   {item['concepto']:<45} {price}")
    if budget["revisar"]:
        out.append("\nPara revisar a mano (no suman al presupuesto):")
        for line in budget["revisar"]:
            best = max(d["conf"] for d in line["danios"])
            out.append(f"   - {line['nombre']}: posible daño ({best:.0%} de confianza)")
    for d in budget.get("descartados_por_no_repetirse", []):
        if d is budget["descartados_por_no_repetirse"][0]:
            out.append("\nDescartados por no repetirse en el video (reflejos o detecciones sueltas):")
        out.append(f"   - {d['nombre']} / {d['categoria']}: en {d['cuadros']} de {d['visible']} cuadros")
    out += ["", "-" * 60, f"TOTAL: $ {budget['total']:,.0f}"]
    if budget["faltan_precios"]:
        out.append("Hay ítems sin precio: completá backend/data/reglas_presupuesto.csv")
    return "\n".join(out)
