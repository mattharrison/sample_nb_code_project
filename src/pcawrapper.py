
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn import decomposition, set_config

set_config(transform_output='pandas')

def components_to_df(pca_components, feature_names):
    idxs = [f'pc{i+1}' for i in range(len(pca_components))]
    return pd.DataFrame(pca_components, columns=feature_names, 
                            index=idxs)

def cols_to_keep(df_, limit):
    return df_.gt(limit).any().pipe(lambda s: s[s]).index

class PCAWrapper:
    def __init__(self):
        pass

    def fit(self, X):
        # write docstring
        """
        Fit PCA to X and add the following attributes:
        - X: the original data
        - pca: the PCA object
        - pcs: the principal components
        - comps: the components as a dataframe
        """
        self.X = X
        # tell scikit-learn to create pandas output
        self.pca = decomposition.PCA()
        # rename columns from pca0 to pca1, pca1 to pca2, etc
        self.pcs = (self.pca.fit_transform(self.X)
                      .rename(columns=lambda col: f'pc{int(col.split("pca")[-1])+1}')
        )
        self.comps = components_to_df(self.pca.components_, self.X.columns)

    def plot_scatter(self, selected_x='pc1', selected_y='pc2', selected_z='pc3', *, selected_color=None,
                     selected_alpha=0.9, selected_size=2, comp_scale=8, cutoff_limit=0.2, additional_data=None):
        """
        Plot a 3D scatter plot of the principal components.

        selected_x, selected_y, selected_z: the columns to plot on the x, y, and z axes
        selected_color: the column to use for the color of the points
        selected_alpha: the opacity of the points
        selected_size: the size of the points
        comp_scale: the scale of the loading vectors
        cutoff_limit: the cutoff limit for the loading vectors
        additional_data: additional data to add to the hover data
        """
        # if selected_color is None, use the first column of the data
        if selected_color is None:
            selected_color = self.pcs.columns[0]   
        if additional_data is not None:
            values = self.pcs.assign(**additional_data)
        else:
            values = self.pcs

        fig = px.scatter_3d(values,
                            x=selected_x, 
                            y=selected_y, 
                            z=selected_z, 
                            color=selected_color,
                            opacity=selected_alpha,
                            hover_data=values.columns, 
                            color_continuous_scale='portland')
        fig.update_traces(marker_size=selected_size)
        fig.update_layout(height=800, width=1000)

        # Center around origin
        max_abs_x = self.pcs[selected_x].abs().max()
        max_abs_y = self.pcs[selected_y].abs().max()
        max_abs_z = self.pcs[selected_z].abs().max()

        # Set the range for each axis based on the maximum absolute value
        fig.update_layout(scene=dict(
            xaxis=dict(nticks=10, range=[-max_abs_x, max_abs_x]),
            yaxis=dict(nticks=10, range=[-max_abs_y, max_abs_y]),
            zaxis=dict(nticks=10, range=[-max_abs_z, max_abs_z]),
        ))

        if comp_scale > 0:
             # Add loading vectors
            comps = self.comps
            num_comps = 3
            loadings = (comps
                .iloc[:num_comps]
                .pipe(lambda df_: df_.loc[:, cols_to_keep(df_, cutoff_limit)])
                .T)

            for name, row_ser in loadings.iterrows():
                fig.add_trace(go.Scatter3d(x=[0, row_ser[selected_x] * comp_scale],
                              y=[0, row_ser[selected_y] * comp_scale],
                              z=[0, row_ser[selected_z] * comp_scale],
                              mode='lines',
                              line={'width':selected_size},
                              showlegend=False,
                             ))
                fig.add_trace(go.Scatter3d(x=[row_ser[selected_x] * comp_scale],
                              y=[row_ser[selected_y] * comp_scale],
                              z=[row_ser[selected_z] * comp_scale],
                              mode='text',
                              text=name,
                              showlegend=False,))
        return fig

    def plot_bar(self, *, component_limit=3, cutoff_limit=0.2):
        """
        Plot a bar chart of the components.

        component_limit: the number of components to plot
        cutoff_limit: the cutoff limit for the loading vectors
        """
        comps = self.comps
        bar_fig = (comps
            .iloc[:component_limit]
            .pipe(lambda df_: df_.loc[:, cols_to_keep(df_, cutoff_limit)])
            .plot.bar(barmode='group')
        )
        return bar_fig

