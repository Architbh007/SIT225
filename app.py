from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load the CSV data
try:
    df = pd.read_csv('t6.csv')
    print("Data loaded successfully")
    print(df.head())  # Print first few rows to verify data
except FileNotFoundError:
    print("Error: The file 't6.csv' was not found.")
    df = pd.DataFrame()  # Create an empty DataFrame to avoid further errors

# If Time column is missing, add a default Time column
if 'Time' not in df.columns:
    df['Time'] = df.index  # Adding default time based on row index

# Initialize the Dash app
app = Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1('Gyroscope Data Visualization'),

    # Dropdown for selecting graph type
    html.Label('Select Graph Type:'),
    dcc.Dropdown(
        id='graph-type',
        options=[
            {'label': 'Scatter Plot', 'value': 'scatter'},
            {'label': 'Line Chart', 'value': 'line'},
            {'label': 'Distribution Plot', 'value': 'distribution'}
        ],
        value='scatter'
    ),

    # Dropdown for selecting data variables
    html.Label('Select Data Variables:'),
    dcc.Dropdown(
        id='data-variables',
        options=[
            {'label': 'X', 'value': 'X'},
            {'label': 'Y', 'value': 'Y'},
            {'label': 'Z', 'value': 'Z'},
            {'label': 'All', 'value': 'all'}
        ],
        value='all'
    ),

    # Input for number of data samples
    html.Label('Number of Data Samples:'),
    dcc.Input(id='num-samples', type='number', value=100, min=1),

    # Button for navigating through data
    html.Button('Previous', id='prev-button', n_clicks=0),
    html.Button('Next', id='next-button', n_clicks=0),

    # Graph for displaying data
    dcc.Graph(id='graph'),

    # Table for displaying data summary
    html.Div(id='summary')
])

# Callback for updating the graph and summary
@app.callback(
    [Output('graph', 'figure'),
     Output('summary', 'children')],
    [Input('graph-type', 'value'),
     Input('data-variables', 'value'),
     Input('num-samples', 'value'),
     Input('prev-button', 'n_clicks'),
     Input('next-button', 'n_clicks')]
)
def update_graph(graph_type, data_variables, num_samples, prev_clicks, next_clicks):
    print("Callback triggered")
    print(f"Graph Type: {graph_type}")
    print(f"Data Variables: {data_variables}")
    print(f"Number of Samples: {num_samples}")
    print(f"Previous Clicks: {prev_clicks}")
    print(f"Next Clicks: {next_clicks}")

    # Handle navigation through data
    start_idx = 0
    if next_clicks > 0:
        start_idx = min(len(df) - num_samples, start_idx + num_samples)
    if prev_clicks > 0:
        start_idx = max(0, start_idx - num_samples)

    # Ensure there are enough samples
    if num_samples > len(df):
        num_samples = len(df)
        
    # Select data
    try:
        data = df.iloc[start_idx:start_idx+num_samples]
        print(data.head())  # Print selected data
    except Exception as e:
        print(f"Error selecting data: {e}")
        data = pd.DataFrame()

    # Handle empty or incorrect data variables
    if data_variables == 'all':
        y_vars = ['X', 'Y', 'Z']
    else:
        y_vars = [data_variables]
    
    # Create the graph
    try:
        if graph_type == 'scatter':
            fig = px.scatter(data, x='Time', y=y_vars)
        elif graph_type == 'line':
            fig = px.line(data, x='Time', y=y_vars)
        elif graph_type == 'distribution':
            if len(y_vars) == 1:
                fig = px.histogram(data, x=y_vars[0])
            else:
                fig = px.histogram(data, x='X')  # Default to X if multiple variables are selected
        else:
            fig = px.scatter(data, x='Time', y='X')  # Default plot if type is unrecognized
    except Exception as e:
        print(f"Error creating graph: {e}")
        fig = px.scatter()  # Return an empty plot if there's an error

    # Create the summary table
    try:
        summary = data.describe().to_html() if not data.empty else "No data available"
    except Exception as e:
        print(f"Error creating summary: {e}")
        summary = "No data available"

    return fig, summary

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
