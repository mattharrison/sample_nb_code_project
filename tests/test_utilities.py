import utilities

import pandas as pd
import pytest

@pytest.fixture
def raw_autos():
    autos_raw = pd.read_csv('https://github.com/mattharrison/datasets/raw/master/data/vehicles.csv.zip',
                   dtype_backend='pyarrow',
                   engine='pyarrow')
    return autos_raw
        


def test_tweak_autos(raw_autos):
    autos = utilities.tweak_autos(raw_autos)
    assert autos is not None
    assert autos.shape == (41144, 15)
    assert autos['year'].dtype == 'int16[pyarrow]'