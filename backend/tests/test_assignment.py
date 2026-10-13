import numpy as np

from carfix.assignment import assign_damages
from carfix.detection import Detection, keep_on_vehicle

from .conftest import box


def test_damage_goes_to_part_with_most_overlap(det, settings):
    parts = [det("Fender", 0, 0, 100, 100), det("Hood", 100, 0, 200, 100)]
    damages = [det("Dent", 20, 20, 60, 60, conf=0.5)]
    assigned, unassigned = assign_damages(parts, damages, settings)
    assert list(assigned) == [("Fender", "Fender")]
    assert assigned[("Fender", "Fender")][0]["categoria"] == "Golpe"
    assert unassigned == []


def test_chapa_neighbour_does_not_get_secondary_damage(det, settings):
    # El daño cae casi todo en el paragolpes y toca un poco el capot.
    parts = [det("Front-bumper", 0, 50, 200, 100), det("Hood", 0, 0, 200, 50)]
    damages = [det("Broken part", 0, 40, 200, 100)]
    assigned, _ = assign_damages(parts, damages, settings)
    assert set(assigned) == {("Front-bumper", "Front-bumper")}


def test_headlight_gets_secondary_damage_only_if_covered_enough(det, settings):
    parts = [det("Fender", 0, 0, 100, 100), det("Headlight", 100, 0, 140, 40)]
    # Cubre el 75% de la óptica -> se le asigna también.
    assigned, _ = assign_damages(parts, [det("Rotura", 50, 0, 130, 60)], settings)
    assert ("Headlight", "Headlight") in assigned
    # Cubre solo el 12% de la óptica -> no.
    assigned, _ = assign_damages(parts, [det("Rotura", 0, 0, 105, 40)], settings)
    assert ("Headlight", "Headlight") not in assigned


def test_repeated_parts_get_numbered(det, settings):
    parts = [det("Headlight", 0, 0, 50, 50), det("Headlight", 150, 0, 200, 50)]
    damages = [det("Rotura", 150, 0, 200, 50)]
    assigned, _ = assign_damages(parts, damages, settings)
    assert list(assigned) == [("Headlight#2", "Headlight")]


def test_damage_outside_any_part_is_unassigned(det, settings):
    assigned, unassigned = assign_damages([det("Hood", 0, 0, 50, 50)], [det("Scratch", 100, 60, 150, 90)], settings)
    assert assigned == {}
    assert unassigned[0]["clase"] == "Scratch"


def test_keep_on_vehicle_drops_background(det):
    vehicle = box(0, 0, 100, 100)
    damages = [det("Rotura", 10, 10, 50, 50), det("Rotura", 150, 10, 190, 50)]
    kept, dropped = keep_on_vehicle(damages, vehicle, min_on_vehicle=0.5)
    assert len(kept) == 1 and dropped == 1
