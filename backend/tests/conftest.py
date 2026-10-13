import numpy as np
import pytest

from carfix.config import Settings
from carfix.detection import Detection
from carfix.rules import load_rules


def box(x0, y0, x1, y1, shape=(100, 200)):
    mask = np.zeros(shape, dtype=bool)
    mask[y0:y1, x0:x1] = True
    return mask


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def rules(settings):
    return load_rules(settings.rules_csv)


@pytest.fixture
def det():
    def make(name, x0, y0, x1, y1, conf=0.9):
        return Detection(name, conf, box(x0, y0, x1, y1))
    return make
