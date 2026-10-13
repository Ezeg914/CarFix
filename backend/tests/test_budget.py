from carfix.budget import CAMBIAR, PINTAR, REPARAR, REVISAR, build_budget, decide


def dmg(categoria, conf, cobertura):
    return {"categoria": categoria, "clase": categoria, "conf": conf, "cobertura": cobertura}


def action(rules, settings, pieza, damages):
    return decide(damages, rules[pieza], settings)[0]


def test_headlight_is_always_replaced(rules, settings):
    assert action(rules, settings, "Headlight", [dmg("Rotura", 0.6, 0.05)]) == CAMBIAR


def test_bumper_any_break_is_replaced(rules, settings):
    assert action(rules, settings, "Front-bumper", [dmg("Rotura", 0.8, 0.05)]) == CAMBIAR


def test_small_break_on_metal_is_repaired(rules, settings):
    assert action(rules, settings, "Hood", [dmg("Rotura", 0.5, 0.03)]) == REPARAR


def test_dent_size_decides_repair_or_replace(rules, settings):
    assert action(rules, settings, "Fender", [dmg("Golpe", 0.5, 0.10)]) == REPARAR
    assert action(rules, settings, "Fender", [dmg("Golpe", 0.5, 0.50)]) == CAMBIAR


def test_paint_only(rules, settings):
    assert action(rules, settings, "Hood", [dmg("Pintura", 0.5, 0.02)]) == PINTAR


def test_low_confidence_goes_to_review(rules, settings):
    assert action(rules, settings, "Hood", [dmg("Rotura", 0.27, 0.18)]) == REVISAR


def test_glass_needs_high_confidence(rules, settings):
    # Reflejos en el parabrisas: 67% no alcanza.
    assert action(rules, settings, "Windshield", [dmg("Rotura", 0.67, 0.96)]) == REVISAR
    assert action(rules, settings, "Windshield", [dmg("Rotura", 0.80, 0.96)]) == CAMBIAR


def test_review_and_ignored_parts_do_not_add_to_total(rules, settings):
    rules = {k: dict(v) for k, v in rules.items()}
    rules["Fender"].update(mano_obra_reparacion=80000, pintura=50000)
    assigned = {
        ("Fender", "Fender"): [dmg("Golpe", 0.5, 0.1)],
        ("Windshield", "Windshield"): [dmg("Rotura", 0.6, 0.9)],
        ("License-plate", "License-plate"): [dmg("Rotura", 0.9, 1.0)],
    }
    budget = build_budget(assigned, [], rules, {"marca": "", "modelo": "", "anio": ""}, settings)
    assert [l["pieza"] for l in budget["piezas"]] == ["Fender"]
    assert [l["pieza"] for l in budget["revisar"]] == ["Windshield"]
    assert budget["total"] == 130000
