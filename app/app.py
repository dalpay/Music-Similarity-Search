#!/usr/bin/env python3
import os
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import sqlalchemy
import pandas as pd
import numpy as np
import faiss

def connect():

    user = os.environ['POSTGRES_UN']
    password = os.environ['POSTGRES_PW']
    host = os.environ['POSTGRES_HN']
    db = 'postgres'
    port = 5432
    url = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(user, password, host, port, db)

    conn = sqlalchemy.create_engine(url, client_encoding='utf8')

    return conn

project_path = '/home/ubuntu/project/processing/'
index_filename = 'msd_gauss.index'
index = faiss.read_index(os.path.join(project_path, index_filename))
conn = connect()

num_initial_rows = 100
initial_query = "SELECT si.name, si.artist, si.year FROM song_info as si LIMIT {}".format(num_initial_rows)
default_df = pd.read_sql_query(initial_query, conn)
default_df['rank'] = np.arange(1, num_initial_rows + 1)
default_df['distance'] = np.zeros(num_initial_rows)
default_df = default_df[['rank', 'distance', 'name', 'artist', 'year']]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([

    html.Div(children=html.H5(children='Music Similarity Search by Deniz Alpay')),
    dcc.Input(
        id='song_name',
        type='text',
        placeholder='Enter a song title'
    ),
    html.Button(id='submit_button', type='submit', children='Submit'),

    html.Div(children=html.H5(children='Most Similar Songs')),
    dash_table.DataTable(
        id='table',
        css=[{
            'selector': '.dash-cell div.dash-cell-value',
            'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
        }],
        columns=[{'name': i, 'id': i} for i in default_df.columns]
    )
])

@app.callback(
    Output(component_id='table', component_property='data'),
    [Input(component_id='submit_button', component_property='n_clicks')],
    [State(component_id='song_name', component_property='value')]
)
def update_table(n_clicks, song_name):
    
    num_neighbors = 20

    # The button was clicked without entering a song name
    if (not song_name):
        return default_df.to_dict('records')

    # Get the vector for the given song name
    song_vector_query = "SELECT sv.vector \
                        FROM song_info as si INNER JOIN song_vectors as sv \
                        ON si.id = sv.id \
                        WHERE si.name='{song_name}'"
    vector_query = song_vector_query.format(song_name=song_name)
    vector_df = pd.read_sql_query(vector_query, conn)
    
    # The song name can't be found in the DB
    if (vector_df.empty):
        return default_df.to_dict('records')
    
    # Run the similarity search on the vector
    vector = vector_df['vector'].values[0]
    vector = np.array(vector, dtype=np.float32)
    vector = np.expand_dims(vector, axis=0)
    dists, ids = index.search(vector, num_neighbors + 1)
    dists = dists[0, 1:]
    ids = ids[0, 1:]
    
    # Get the song info of the most similar songs
    song_info_query = "SELECT si.id, si.name, si.artist, si.year \
                    FROM song_info as si \
                    WHERE si.id in "
    ids_format = "{}," * num_neighbors
    song_info_query += '(' + ids_format[:-1] + ')'
    song_query = song_info_query.format(*ids)
    song_df = pd.read_sql_query(song_query, conn)
    
    # Add distances and ranks
    num_results = len(song_df)
    song_df['rank'] = 0
    song_df['distance'] = 0.0
    for rank, (id, dist) in enumerate(zip(ids, dists)):
        song_df.loc[song_df['id'] == id, 'rank'] = rank + 1
        song_df.loc[song_df['id'] == id, 'distance'] = dist
    song_df.sort_values(by=['rank'], inplace=True)
    song_df = song_df[['rank', 'distance', 'name', 'artist', 'year']]

    return song_df.to_dict('records')

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port='5000')
