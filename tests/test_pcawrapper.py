# write pytests for pcawrapper.py

import pandas as pd
import pytest

from pcawrapper import PCAWrapper

@pytest.fixture
def X():
    return pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]})

def test_pcawrapper_create():
    pca = PCAWrapper()
    assert pca is not None

def test_pcawrapper_fit(X):
    pca = PCAWrapper()
    pca.fit(X)
    assert pca.X is not None
    assert pca.pca is not None
    assert pca.pcs is not None
    assert pca.comps is not None

def test_pcawrapper_plot_scatter(X):
    pca = PCAWrapper()
    pca.fit(X)
    pca.plot_scatter()
    assert pca.pcs is not None
    assert pca.comps is not None

        