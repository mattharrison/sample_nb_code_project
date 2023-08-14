from feature_engine import encoding

import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn import base, compose, pipeline, preprocessing, set_config
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline

pd.options.plotting.backend = 'plotly'
set_config(transform_output='pandas')
#set_config(transform_output='default')

def tweak_autos(autos):
    cols = ['city08', 'comb08', 'highway08', 'cylinders', 'displ', 'drive', 'eng_dscr', 
        'fuelCost08', 'make', 'model', 'trany', 'range', 'createdOn', 'year']
    return (autos
     [cols]
     .assign(cylinders=autos.cylinders.fillna(0).astype('int8[pyarrow]'),
             displ=autos.displ.fillna(0).astype('float32[pyarrow]'),
             drive=autos.drive.replace('', 'Other').astype('category'),
             automatic=autos.trany.astype(str).str.contains('Auto'),
             speeds=autos.trany.astype(str).str.extract(r'(\d+)').fillna('20').astype('int8[pyarrow]'),
             createdOn=pd.to_datetime(autos
                .createdOn
                .replace({' EDT': ' -0400', ' EST': ' -0500'}, regex=True),
                          format='%a %b %d %H:%M:%S %z %Y', utc=True)
                .dt.tz_convert('America/New_York'),
             ffs=autos.eng_dscr.str.contains('FFS')
            )
     .astype({'highway08': 'int8[pyarrow]', 'city08': 'int16[pyarrow]', 'comb08': 'int16[pyarrow]', 'fuelCost08': 'int16[pyarrow]',
              'range': 'int16[pyarrow]',  'year': 'int16[pyarrow]', 'make': 'category',
              'model': 'category'})
     .loc[:, ['city08', 'comb08', 'highway08', 'cylinders', 'displ', 'drive',
       'fuelCost08', 'make', 'model', 'range', 'createdOn', 'year',
       'automatic', 'speeds', 'ffs']]
    )


def feature_engineer(df):
    return (df
      .assign(customer_age=pd.Timestamp('today').year - df.year_of_birth,
              membership_duration=(pd.Timestamp('today') - df['parent_account_opening_date']).dt.days,
             )
           )

class FeatureEngineerTransformer(base.BaseEstimator, base.TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return feature_engineer(X)

def get_pipeline(categorical_features, numeric_features, feature_transformer=None):

    num_pipeline = pipeline.Pipeline(steps=[
        ('std', preprocessing.StandardScaler())
    ])

    cat_pipeline = pipeline.Pipeline(steps=[
        ('oh', encoding.OneHotEncoder(top_categories=5, drop_last=True))
    ])

    pipe = pipeline.Pipeline(steps=[])
    if feature_transformer:
        pipe.steps.append(('feat', FeatureEngineerTransformer()))
    pipe.steps.extend([
        ('ct', compose.ColumnTransformer(transformers=[
            ('num', num_pipeline, numeric_features),
            ('cat', cat_pipeline, categorical_features),
            ])),
      ]
    )
    return pipe

def get_pca_pipeline():
    scaler = StandardScaler()
    pca = PCA()
    pipeline = make_pipeline(scaler, pca)
    return pipeline

