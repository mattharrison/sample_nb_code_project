# dash app to display the pca results
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

from utilities import tweak_autos, feature_engineer, get_pipeline, get_pca_pipeline
import pcawrapper as pw

def get_app(data, categorical_features, numeric_features):
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.title = 'PCA Explorer'
    pipe = get_pipeline(categorical_features, numeric_features)
    X = pipe.fit_transform(data)
    pca = pw.PCAWrapper()
    pca.fit(X)

    scatter_controls = dbc.Card([
            html.Div(
                [
                    dbc.Label("Color By:"),
                    dcc.Dropdown(
                        id='scatter-color-dropdown',
                        options=[{'label': i, 'value': i} for i in data.columns],
                        value=data.columns[0]
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("X-Axis:"),
                    dcc.Dropdown(
                        id='scatter-x-dropdown',
                        options=[{'label': i, 'value': i} for i in pca.pcs.columns],
                        value='pc1'
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Y-Axis:"),
                    dcc.Dropdown(
                        id='scatter-y-dropdown',
                        options=[{'label': i, 'value': i} for i in pca.pcs.columns],
                        value='pc2'
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Z-Axis:"),
                    dcc.Dropdown(
                        id='scatter-z-dropdown',
                        options=[{'label': i, 'value': i} for i in pca.pcs.columns],
                        value='pc3'
                    ),
                ]
            ),
             html.Div(
            [
                dbc.Label("Alpha:"),
                dbc.Input(id='scatter-alpha-dropdown', type="number", min=0.05, max=1, step=.05, value=.90)
                
                ]
            ),
            html.Div(
                [
                    dbc.Label("Size:"),
                    dbc.Input(id='scatter-size-dropdown', type="number", min=0.5, max=15, step=.3, value=2)
                ]
            ),
             html.Div(
                [
                    dbc.Label("Component Scaling:"),
                    dbc.Input(id='comp-scale', type="number", min=0, max=15, step=1, value=8)
                ]
            ),
        ],
        body=True,
    )

    bar_controls = dbc.Card(
        [
            html.Div(
                [
                    dbc.Label("Component Limit:"),
                    dcc.Slider(
                        id='component-limit-slider',
                        min=1,
                        max=len(pca.comps),
                        step=1,
                        value=3
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Cutoff Limit:"),
                    dbc.Input(id='cutoff-limit-slider', type="number", min=0.05, max=.7, step=.03, value=.2)                   
                ]
            ),
        ],
        body=True,
    )
  
    app.layout = dbc.Container(
        [
            html.H1("PCA Plotly Demo"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(scatter_controls, md=4),
                    dbc.Col(dcc.Graph(id="scatter-graph", 
                                     ), md=8),
                ],
                align="center",
            ),
            dbc.Row(
                [
                    dbc.Col(bar_controls, md=4),                    
                    dbc.Col(dcc.Graph(id="bar-graph", 
                                     ), md=8),
                ]
            )
        ],
        fluid=True,
    )

    @app.callback( Output('scatter-graph', 'figure'),
        [Input('scatter-color-dropdown', 'value'),
         Input('scatter-x-dropdown', 'value'),
         Input('scatter-y-dropdown', 'value'),
         Input('scatter-z-dropdown', 'value'),
         Input('scatter-alpha-dropdown', 'value'),
         Input('scatter-size-dropdown', 'value'),
         Input('comp-scale', 'value'),         
         Input('cutoff-limit-slider', 'value')]         
    )
    def update_scatter(color, x, y, z, alpha, size, comp_scale, cutoff):
        fig = pca.plot_scatter(x, y, z, selected_color=color,
                               selected_alpha=alpha, selected_size=size, 
                               comp_scale=comp_scale, cutoff_limit=cutoff,
                               additional_data=data)
        return fig
    
    @app.callback(
        Output('bar-graph', 'figure'),
        [Input('component-limit-slider', 'value'),
         Input('cutoff-limit-slider', 'value')]
    )
    def update_bar(limit, cutoff):
        fig = pca.plot_bar(component_limit=limit,  cutoff_limit=cutoff)
        return fig
    
    return app

if __name__ == '__main__':
    autos_raw = pd.read_csv('https://github.com/mattharrison/datasets/raw/master/data/vehicles.csv.zip',
                   dtype_backend='pyarrow',
                   engine='pyarrow')
    # drop date, convert pyarrow strings to categories
    autos = (tweak_autos(autos_raw)
            .loc[:, ['city08', 'comb08', 'highway08', 'cylinders', 'displ', 'drive',
        'fuelCost08', 'make', 'model', 'range', 'year',
        'automatic', 'speeds', 'ffs']]
            )
    numerical_columns = list(autos.select_dtypes('number').columns)
    categorical_columns = [c for c in autos.columns if c not in numerical_columns]
    app = get_app(autos, categorical_columns, numerical_columns)
    app.run_server(debug=True)
