import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import numpy as np
import base64
import io
from PIL import Image
import tempfile

# Import your simulation functions
from simulation import Agent, moveAgents, rollInfect, trackCounts, getPosition, getInfected

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1("Disease Spread Simulation Dashboard"),
    
    html.Div([
        html.Div([
            html.H3("Simulation Parameters"),
            
            html.Label("Number of Agents:"),
            dcc.Slider(
                id='num-agents-slider',
                min=50, max=1000, step=50, value=500,
                marks={i: str(i) for i in range(0, 1001, 200)}
            ),
            
            html.Label("Initial Infected:"),
            dcc.Slider(
                id='initial-infected-slider',
                min=1, max=50, step=1, value=10,
                marks={i: str(i) for i in range(0, 51, 10)}
            ),
            
            html.Label("Agent Resistance (0-1):"),
            dcc.Slider(
                id='resistance-slider',
                min=0, max=1, step=0.05, value=0.3,
                marks={i/10: str(i/10) for i in range(0, 11, 2)}
            ),
            
            html.Label("Proximity Threshold:"),
            dcc.Slider(
                id='proximity-slider',
                min=1, max=30, step=1, value=10,
                marks={i: str(i) for i in range(0, 31, 5)}
            ),
            
            html.Label("Step Size:"),
            dcc.Slider(
                id='step-size-slider',
                min=1, max=10, step=0.5, value=5,
                marks={i: str(i) for i in range(1, 11, 1)}
            ),
            
            html.Label("Number of Timesteps:"),
            dcc.Slider(
                id='timesteps-slider',
                min=100, max=1000, step=100, value=500,
                marks={i: str(i) for i in range(0, 1001, 200)}
            ),
            
            html.Button('Run Simulation', id='run-button', n_clicks=0),
        ], style={'width': '30%', 'padding': '20px', 'display': 'inline-block', 'vertical-align': 'top'}),
        
        html.Div([
            html.H3("Simulation Results"),
            
            dcc.Tabs([
                dcc.Tab(label='Current State', children=[
                    dcc.Graph(id='current-state-graph')
                ]),
                dcc.Tab(label='Disease Progression', children=[
                    dcc.Graph(id='disease-progression-graph')
                ]),
                dcc.Tab(label='Animation', children=[
                    html.Img(id='animation-gif')
                ])
            ])
        ], style={'width': '65%', 'padding': '20px', 'display': 'inline-block'})
    ])
])

# Define callback to run simulation and update graphs
@app.callback(
    [Output('current-state-graph', 'figure'),
     Output('disease-progression-graph', 'figure'),
     Output('animation-gif', 'src')],
    [Input('run-button', 'n_clicks')],
    [State('num-agents-slider', 'value'),
     State('initial-infected-slider', 'value'),
     State('resistance-slider', 'value'),
     State('proximity-slider', 'value'),
     State('step-size-slider', 'value'),
     State('timesteps-slider', 'value')]
)
def run_and_display_simulation(n_clicks, num_agents, num_initial_infected, 
                              resistance, proximity, step_size, timesteps):
    if n_clicks == 0:
        # Return empty figures for initial load
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Run simulation to see results")
        return empty_fig, empty_fig, ""
    
    # Initialize agents
    agents = []
    bounds = (0, 500)
    for i in range(num_agents):
        x = np.random.uniform(bounds[0], bounds[1])
        y = np.random.uniform(bounds[0], bounds[1])
        agents.append(Agent(x, y, False, resistance))

    for i in range(min(num_initial_infected, num_agents)):
        agents[i].infected = True
        agents[i].infectedCounter = 50

    frames = []
    statistics = []
    
    # Run simulation
    for i in range(timesteps):
        agents = moveAgents(agents, step_size, bounds, bounds)
        agents = rollInfect(agents, proximity)
        positions = getPosition(agents)
        infected = getInfected(agents)
        
        frames.append([positions[:, 0], positions[:, 1], infected])
        infected_count, immune_count, healthy_count = trackCounts(agents)
        statistics.append((infected_count, immune_count, healthy_count))
    
    # Create current state figure (last frame)
    last_frame = frames[-1]
    current_fig = go.Figure()
    
    # Add scatter plot for each agent type
    positions = np.column_stack((last_frame[0], last_frame[1]))
    infected = last_frame[2]
    
    # Extract positions for different agent types
    infected_pos = positions[infected]
    immune_pos = positions[[agent.immunity for agent in agents]]
    healthy_pos = positions[[(not agent.infected and not agent.immunity) for agent in agents]]
    
    if len(infected_pos) > 0:
        current_fig.add_trace(go.Scatter(
            x=infected_pos[:, 0], y=infected_pos[:, 1], 
            mode='markers', name='Infected',
            marker=dict(color='red', size=8)
        ))
    
    if len(immune_pos) > 0:
        current_fig.add_trace(go.Scatter(
            x=immune_pos[:, 0], y=immune_pos[:, 1], 
            mode='markers', name='Immune',
            marker=dict(color='blue', size=8)
        ))
    
    if len(healthy_pos) > 0:
        current_fig.add_trace(go.Scatter(
            x=healthy_pos[:, 0], y=healthy_pos[:, 1], 
            mode='markers', name='Healthy',
            marker=dict(color='green', size=8)
        ))
    
    current_fig.update_layout(
        title="Current State (Last Timestep)",
        xaxis=dict(range=[0, 500]), 
        yaxis=dict(range=[0, 500]),
        height=500
    )
    
    # Create disease progression figure
    infected, immune, healthy = zip(*statistics)
    
    progression_fig = go.Figure()
    progression_fig.add_trace(go.Scatter(
        x=list(range(timesteps)), y=infected, 
        mode='lines', name='Infected',
        line=dict(color='red', width=2)
    ))
    progression_fig.add_trace(go.Scatter(
        x=list(range(timesteps)), y=immune, 
        mode='lines', name='Immune',
        line=dict(color='blue', width=2)
    ))
    progression_fig.add_trace(go.Scatter(
        x=list(range(timesteps)), y=healthy, 
        mode='lines', name='Healthy',
        line=dict(color='green', width=2)
    ))
    
    progression_fig.update_layout(
        title="Disease Progression Over Time",
        xaxis_title="Timestep",
        yaxis_title="Number of Agents",
        height=500
    )
    
    # Create animation (this is simplified - you may need to adapt your makeGif function)
    # For simplicity, we'll just use the last frame as a static image
    # In a full implementation, you'd generate the GIF and encode it for display
    
    animation_src = ""  # Placeholder for where you'd put the actual GIF encoding
    
    return current_fig, progression_fig, animation_src

if __name__ == '__main__':
    app.run_server(debug=True)