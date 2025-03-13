import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import numpy as np

from simulation import Agent, moveAgents, rollInfect, trackCounts, getPosition, getInfected


app = dash.Dash(__name__)


app.layout = html.Div([
    html.H1("MSDS 460 Final Project: Agent-Based Disease Simulation Dashboard"),
    
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
                    html.Div(id='animation-container', children=[
                        dcc.Graph(id='animation-frame'),
                        html.Div([
                            html.Button('Previous', id='prev-button', n_clicks=0),
                            html.Button('Play/Pause', id='play-button', n_clicks=0),
                            html.Button('Next', id='next-button', n_clicks=0),
                            html.Div(id='frame-indicator')
                        ], style={'textAlign': 'center', 'marginTop': '10px'}),
                        dcc.Interval(
                            id='animation-interval',
                            interval=200, 
                            n_intervals=0,
                            disabled=True
                        )
                    ])
                ])
            ])
        ], style={'width': '65%', 'padding': '20px', 'display': 'inline-block'})
    ])
])

simulation_data = {
    'frames': [],
    'statistics': [],
    'current_frame': 0,
    'playing': False
}

@app.callback(
    [Output('current-state-graph', 'figure'),
     Output('disease-progression-graph', 'figure'),
     Output('animation-frame', 'figure'),
     Output('frame-indicator', 'children'),
     Output('animation-interval', 'disabled')],
    [Input('run-button', 'n_clicks'),
     Input('prev-button', 'n_clicks'),
     Input('next-button', 'n_clicks'),
     Input('play-button', 'n_clicks'),
     Input('animation-interval', 'n_intervals')],
    [State('num-agents-slider', 'value'),
     State('initial-infected-slider', 'value'),
     State('resistance-slider', 'value'),
     State('proximity-slider', 'value'),
     State('step-size-slider', 'value'),
     State('timesteps-slider', 'value'),
     State('animation-interval', 'disabled')]
)
def update_simulation(run_clicks, prev_clicks, next_clicks, play_clicks, 
                     n_intervals, num_agents, num_initial_infected, 
                     resistance, proximity, step_size, timesteps, interval_disabled):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'no-trigger'
    
    if run_clicks == 0 and trigger_id == 'run-button':

        empty_fig = go.Figure()
        empty_fig.update_layout(title="Run simulation to see results")
        return empty_fig, empty_fig, empty_fig, "No simulation data", True
    

    if trigger_id == 'run-button':
        simulation_data['current_frame'] = 0
        simulation_data['playing'] = False
        
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
        

        for i in range(timesteps):
            agents = moveAgents(agents, step_size, bounds, bounds)
            agents = rollInfect(agents, proximity)
            positions = getPosition(agents)
            infected = getInfected(agents)
            
            frames.append((positions, infected, [agent.immunity for agent in agents]))
            infected_count, immune_count, healthy_count = trackCounts(agents)
            statistics.append((infected_count, immune_count, healthy_count))

        simulation_data['frames'] = frames
        simulation_data['statistics'] = statistics
    

    elif trigger_id == 'play-button' and simulation_data['frames']:
        simulation_data['playing'] = not simulation_data['playing']
    elif trigger_id == 'next-button' and simulation_data['frames']:
        simulation_data['current_frame'] = min(simulation_data['current_frame'] + 1, len(simulation_data['frames']) - 1)
    elif trigger_id == 'prev-button' and simulation_data['frames']:
        simulation_data['current_frame'] = max(simulation_data['current_frame'] - 1, 0)
    elif trigger_id == 'animation-interval' and simulation_data['frames'] and simulation_data['playing']:

        if simulation_data['current_frame'] >= len(simulation_data['frames']) - 1:
            simulation_data['current_frame'] = 0
        else:
            simulation_data['current_frame'] += 1
    
    if not simulation_data['frames']:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Run simulation to see results")
        return empty_fig, empty_fig, empty_fig, "No simulation data", True
    

    last_frame = simulation_data['frames'][-1]
    current_fig = create_state_figure(last_frame, "Current State (Last Timestep)")
    

    progression_fig = create_progression_figure(simulation_data['statistics'], timesteps)

    current_frame_idx = simulation_data['current_frame']
    animation_fig = create_state_figure(
        simulation_data['frames'][current_frame_idx], 
        f"Timestep: {current_frame_idx + 1}"
    )
    frame_indicator = f"Frame {current_frame_idx + 1} of {len(simulation_data['frames'])}"
    interval_disabled = not simulation_data['playing']
    
    return current_fig, progression_fig, animation_fig, frame_indicator, interval_disabled

def create_state_figure(frame_data, title):
    positions, infected, immunity = frame_data
    fig = go.Figure()

    positions_np = np.array(positions)
    infected_np = np.array(infected)
    immunity_np = np.array(immunity)

    infected_pos = positions_np[infected_np]
    immune_pos = positions_np[immunity_np]
    healthy_pos = positions_np[~infected_np & ~immunity_np]
    
    if len(infected_pos) > 0:
        fig.add_trace(go.Scatter(
            x=infected_pos[:, 0], y=infected_pos[:, 1], 
            mode='markers', name='Infected',
            marker=dict(color='red', size=8)
        ))
    
    if len(immune_pos) > 0:
        fig.add_trace(go.Scatter(
            x=immune_pos[:, 0], y=immune_pos[:, 1], 
            mode='markers', name='Immune',
            marker=dict(color='blue', size=8)
        ))
    
    if len(healthy_pos) > 0:
        fig.add_trace(go.Scatter(
            x=healthy_pos[:, 0], y=healthy_pos[:, 1], 
            mode='markers', name='Healthy',
            marker=dict(color='green', size=8)
        ))
    
    fig.update_layout(
        title=title,
        xaxis=dict(range=[0, 500], showticklabels=False), 
        yaxis=dict(range=[0, 500], showticklabels=False),
        height=500
    )
    
    return fig

def create_progression_figure(statistics, timesteps):
    infected, immune, healthy = zip(*statistics)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(statistics))), y=infected, 
        mode='lines', name='Infected',
        line=dict(color='red', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=list(range(len(statistics))), y=immune, 
        mode='lines', name='Immune',
        line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=list(range(len(statistics))), y=healthy, 
        mode='lines', name='Healthy',
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title="Disease Progression Over Time",
        xaxis_title="Timestep",
        yaxis_title="Number of Agents",
        height=500
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)