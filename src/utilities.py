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


def tweak_cust(df):
    column_mapping = {
	"datum_datenabzug": "data_extraction_date",
	"stdp_stammnr": "parent_account_id",
	"stdp_eroeffnung": "parent_account_opening_date",
	"kund_stammnr": "client_number",
	"anrede": "salutation",
	"titel": "academic_title",
	"strasse": "street",
	"plz": "zip",
	"ort": "city",
	"kund_geloescht": "customer_deleted_flag",
	"kund_geloescht_datum": "customer_deleted_date",
	"kund_emailadresse": "email_address",
	"dbt_valid_from": "record_technical_valid_from_date",
	"dbt_valid_to": "record_technical_valid_until_date",
	"geburtsdatum_jahr": "year_of_birth",
	"geburtsdatum_mon": "month_of_birth"
    }
    return (df
        .rename(columns=column_mapping)
        .pipe(lambda df_:
          df_
            .assign(data_extraction_date=pd.to_datetime(df_.data_extraction_date),
                    parent_account_opening_date=pd.to_datetime(df_.parent_account_opening_date, format='%d-%m-%Y'),
                    customer_deleted_date=pd.to_datetime(df_.customer_deleted_date, format='%d-%m-%Y'),
                    record_technical_valid_from_date=pd.to_datetime(df_.record_technical_valid_from_date, format='%Y-%m-%d'),                    
                    record_technical_valid_until_date=pd.to_datetime(df_.record_technical_valid_until_date, format='%Y-%m-%d'),                    
                   )
             )
        .astype({'salutation': 'category',
                'academic_title': 'category',
                'city': 'category',
                'zip': 'category',
                'year_of_birth': 'int16[pyarrow]',
                'month_of_birth': 'int8[pyarrow]',
                })
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

