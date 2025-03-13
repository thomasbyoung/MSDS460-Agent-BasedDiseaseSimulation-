import dash
from dash import dcc, html, Input, Output, State, ctx
import plotly.graph_objs as go
import numpy as np

# Import only what's available in your simulation.py
from simulation import Agent

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define color mapping for agent states
COLOR_MAP = {
    'healthy': '#00cc00',  # Green
    'infected': '#ff0000',  # Red
    'immune': '#0066ff',   # Blue
}

# Extend the Agent class with tracking capabilities
class TrackedAgent(Agent):
    def __init__(self, agent_id, x, y, infected, resistance, immunity=False, immunityCounter=0, infectedCounter=0, vaccinated=False):
        super().__init__(x, y, infected, resistance, immunity, immunityCounter, infectedCounter, vaccinated)
        self.id = agent_id
        self.state_history = []
        self.record_state()
    
    def record_state(self):
        if self.infected:
            state = 'infected'
        elif self.immunity:
            state = 'immune'
        else:
            state = 'healthy'
        self.state_history.append(state)
        
    # Override the movement method to track state changes
    def movement(self, stepSize, xBounds, yBounds):
        previous_state = 'infected' if self.infected else 'immune' if self.immunity else 'healthy'
        
        # Call the original movement method
        super().movement(stepSize, xBounds, yBounds)
        
        # Check if state changed and record if it did
        current_state = 'infected' if self.infected else 'immune' if self.immunity else 'healthy'
        if current_state != previous_state:
            self.record_state()
    
    # Override the infect method to track infection events
    def infect(self):
        was_infected = self.infected
        
        # Call the original infect method
        super().infect()
        
        # Record state change if infected
        if not was_infected and self.infected:
            self.record_state()

# Define the app layout
app.layout = html.Div([
    html.H1("MSDS 460 Agent-Based Disease Simulation Dashboard", 
           style={'textAlign': 'center', 'margin': '20px 0'}),
    
    html.Div([
        html.Div([
            html.H3("Simulation Parameters"),
            
            html.Label("Number of Agents:"),
            dcc.Slider(
                id='num-agents-slider',
                min=50, max=500, step=50, value=200,
                marks={i: str(i) for i in range(0, 501, 100)}
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
                min=100, max=500, step=50, value=200,
                marks={i: str(i) for i in range(0, 501, 100)}
            ),
            
            html.Button('Run Simulation', id='run-button', n_clicks=0,
                      style={'margin-top': '20px', 'background-color': '#4CAF50', 
                             'color': 'white', 'border': 'none', 'padding': '10px 20px',
                             'border-radius': '5px', 'cursor': 'pointer'}),
            
            html.Div(id='loading-text', style={'margin-top': '10px', 'color': '#ff5722', 'font-weight': 'bold'})
        ], style={'width': '25%', 'padding': '20px', 'display': 'inline-block', 'vertical-align': 'top'}),
        
        html.Div([
            html.H3("Simulation Results"),
            
            dcc.Tabs([
                dcc.Tab(label='Current State', children=[
                    dcc.Graph(id='current-state-graph', style={'height': '600px'})
                ]),
                dcc.Tab(label='Disease Progression', children=[
                    dcc.Graph(id='disease-progression-graph', style={'height': '600px'})
                ]),
                dcc.Tab(label='Animation', children=[
                    dcc.Graph(id='animation-frame', style={'height': '600px'}),
                    html.Div([
                        html.Button('◀ Previous', id='prev-button', n_clicks=0, 
                                  style={'margin': '0 10px', 'padding': '5px 15px'}),
                        html.Button('▶ Play/Pause', id='play-button', n_clicks=0,
                                  style={'margin': '0 10px', 'padding': '5px 15px', 
                                        'background-color': '#2196F3', 'color': 'white',
                                        'border-radius': '4px', 'border': 'none'}),
                        html.Button('▶ Next', id='next-button', n_clicks=0,
                                  style={'margin': '0 10px', 'padding': '5px 15px'}),
                    ], style={'textAlign': 'center', 'marginTop': '15px'}),
                    html.Div(id='frame-indicator', style={'textAlign': 'center', 'marginTop': '10px', 'fontWeight': 'bold'}),
                    dcc.Interval(
                        id='animation-interval',
                        interval=200,
                        n_intervals=0,
                        disabled=True
                    )
                ]),
                dcc.Tab(label='Agent Timeline', children=[
                    html.Div([
                        html.H4("Agent State Timeline", style={'textAlign': 'center'}),
                        html.P("Showing state changes for agents over time. Each column represents a state change event.", 
                               style={'textAlign': 'center'}),
                        html.Div([
                            html.Div([
                                html.Span("● Healthy", style={'color': COLOR_MAP['healthy'], 'margin-right': '20px', 'font-weight': 'bold'}),
                                html.Span("● Infected", style={'color': COLOR_MAP['infected'], 'margin-right': '20px', 'font-weight': 'bold'}),
                                html.Span("● Immune", style={'color': COLOR_MAP['immune'], 'margin-right': '20px', 'font-weight': 'bold'})
                            ], style={'textAlign': 'center', 'margin': '10px'})
                        ]),
                        html.Div(id='agent-timeline-table'),
                        html.Div([
                            html.Button('Show More Agents', id='show-more-button', n_clicks=0,
                                      style={'margin': '20px 10px', 'padding': '5px 15px'})
                        ], style={'textAlign': 'center'})
                    ])
                ])
            ])
        ], style={'width': '70%', 'padding': '20px', 'display': 'inline-block'})
    ])
])

# Store simulation data globally 
stored_data = {
    'frames': [],
    'statistics': [],
    'agents': [],
    'current_frame': 0,
    'playing': False,
    'visible_agents': 20
}

# Reimplementing needed functions from your simulation.py
def getPosition(agents):
    positions = []
    for agent in agents:
        positions.append([agent.x, agent.y])
    return np.array(positions)

def getInfected(agents):
    infected = []
    for agent in agents:
        infected.append(agent.infected)
    return np.array(infected)

def trackCounts(agents):
    infected = sum(1 for agent in agents if agent.infected)
    immune = sum(1 for agent in agents if agent.immunity)
    healthy = sum(1 for agent in agents if not agent.infected and not agent.immunity)
    return infected, immune, healthy

def getCloseAgents(distanceMatrix, agentNumber, proximity_threshold=10):
    sort = np.argsort(distanceMatrix[agentNumber])
    closeMask = distanceMatrix[agentNumber][sort] < proximity_threshold
    closeAgents = np.argsort(distanceMatrix[agentNumber])[closeMask][1:]
    return closeAgents

def moveAgents(agents, stepSize, xBounds, yBounds):
    for agent in agents:
        agent.movement(stepSize, xBounds, yBounds)
    return agents

def rollInfect(agents, proximity_threshold=10):
    positions = getPosition(agents)
    distanceMatrix = np.zeros((len(agents), len(agents)))
    
    # Calculate distances between all agents
    for i in range(len(agents)):
        for j in range(i+1, len(agents)):
            dist = np.sqrt(np.sum((positions[i] - positions[j])**2))
            distanceMatrix[i, j] = dist
            distanceMatrix[j, i] = dist
    
    for i in range(len(agents)):
        closeAgents = getCloseAgents(distanceMatrix, i, proximity_threshold)
        for j in closeAgents:
            if agents[j].infected and not agents[i].immunity:
                agents[i].infect()
    return agents

# Helper function to run simulation with tracked agents
def run_tracked_simulation(num_agents, num_initial_infected, resistance, step_size, bounds, timesteps, proximity):
    # Initialize agents with IDs
    agents = []
    for i in range(num_agents):
        x = np.random.uniform(bounds[0], bounds[1])
        y = np.random.uniform(bounds[0], bounds[1])
        agents.append(TrackedAgent(i+1, x, y, False, resistance))
    
    # Set initial infected agents
    for i in range(min(num_initial_infected, num_agents)):
        agents[i].infected = True
        agents[i].infectedCounter = 50
        agents[i].record_state()
        
    frames = []
    statistics = []
    
    # Run simulation steps
    for i in range(timesteps):
        agents = moveAgents(agents, step_size, bounds, bounds)
        agents = rollInfect(agents, proximity)
        positions = getPosition(agents)
        infected = getInfected(agents)
        
        frames.append({
            'positions': positions,
            'infected': infected,
            'immunity': [agent.immunity for agent in agents],
            'agent_ids': [agent.id for agent in agents]
        })
        
        infected_count, immune_count, healthy_count = trackCounts(agents)
        statistics.append((infected_count, immune_count, healthy_count))
    
    return frames, statistics, agents

# Callback for loading indicator
@app.callback(
    Output('loading-text', 'children'),
    [Input('run-button', 'n_clicks'),
     Input('current-state-graph', 'figure')]
)
def update_loading_text(n_clicks, figure):
    if n_clicks > 0 and ctx.triggered_id == 'run-button':
        return "Running simulation... Please wait."
    return ""

# Callback for Current State and Disease Progression graphs
@app.callback(
    [Output('current-state-graph', 'figure'),
     Output('disease-progression-graph', 'figure')],
    Input('run-button', 'n_clicks'),
    [State('num-agents-slider', 'value'),
     State('initial-infected-slider', 'value'),
     State('resistance-slider', 'value'),
     State('proximity-slider', 'value'),
     State('step-size-slider', 'value'),
     State('timesteps-slider', 'value')]
)
def update_main_graphs(n_clicks, num_agents, num_initial_infected, 
                      resistance, proximity, step_size, timesteps):
    # Create empty figures for initial load
    if n_clicks == 0:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Run simulation to see results")
        return empty_fig, empty_fig
    
    # Run the simulation with agent tracking
    bounds = (0, 500)
    frames, statistics, agents = run_tracked_simulation(
        num_agents=num_agents,
        num_initial_infected=num_initial_infected,
        resistance=resistance,
        step_size=step_size,
        bounds=bounds,
        timesteps=timesteps,
        proximity=proximity
    )
    
    # Store data globally
    stored_data['frames'] = frames
    stored_data['statistics'] = statistics
    stored_data['agents'] = agents
    stored_data['current_frame'] = 0
    stored_data['playing'] = False
    stored_data['visible_agents'] = min(20, num_agents)
    
    # Create the current state figure (last frame)
    last_frame = frames[-1]
    current_fig = create_state_figure(
        last_frame['positions'], 
        last_frame['infected'], 
        last_frame['immunity'],
        last_frame.get('agent_ids', range(len(last_frame['positions']))),
        "Final State (Last Timestep)"
    )
    
    # Create the disease progression figure
    progression_fig = create_progression_figure(statistics)
    
    return current_fig, progression_fig

# Callback for animation frame
@app.callback(
    [Output('animation-frame', 'figure'),
     Output('frame-indicator', 'children'),
     Output('animation-interval', 'disabled')],
    [Input('prev-button', 'n_clicks'),
     Input('next-button', 'n_clicks'),
     Input('play-button', 'n_clicks'),
     Input('animation-interval', 'n_intervals'),
     Input('run-button', 'n_clicks')]
)
def update_animation_frame(prev_clicks, next_clicks, play_clicks, n_intervals, run_clicks):
    # Get triggered button
    triggered_id = ctx.triggered_id if ctx.triggered_id else 'no-id'
    
    # Toggle play state
    if triggered_id == 'play-button' and stored_data['frames']:
        stored_data['playing'] = not stored_data['playing']
    
    # Handle button clicks for frame navigation
    if triggered_id == 'prev-button' and stored_data['frames']:
        stored_data['current_frame'] = max(0, stored_data['current_frame'] - 1)
    elif triggered_id == 'next-button' and stored_data['frames']:
        stored_data['current_frame'] = min(len(stored_data['frames']) - 1, stored_data['current_frame'] + 1)
    elif triggered_id == 'run-button':
        stored_data['current_frame'] = 0
        stored_data['playing'] = False
    elif triggered_id == 'animation-interval' and stored_data['playing'] and stored_data['frames']:
        # Loop back to beginning when reaching the end
        if stored_data['current_frame'] >= len(stored_data['frames']) - 1:
            stored_data['current_frame'] = 0
        else:
            stored_data['current_frame'] += 1
    
    # If no frames available yet, return empty figure
    if not stored_data['frames']:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Run simulation to see frames")
        return empty_fig, "No frames available", True
    
    # Get current frame data
    current_idx = stored_data['current_frame']
    current_frame = stored_data['frames'][current_idx]
    
    # Create figure for current animation frame
    fig = create_state_figure(
        current_frame['positions'],
        current_frame['infected'],
        current_frame['immunity'],
        current_frame.get('agent_ids', range(len(current_frame['positions']))),
        f"Timestep: {current_idx + 1}"
    )
    
    # Frame indicator text
    frame_text = f"Frame {current_idx + 1} of {len(stored_data['frames'])}"
    
    # Return figure, frame text, and interval disabled state
    return fig, frame_text, not stored_data['playing']

# Callback for Agent Timeline Table
@app.callback(
    Output('agent-timeline-table', 'children'),
    [Input('run-button', 'n_clicks'),
     Input('show-more-button', 'n_clicks')]
)
def update_agent_timeline(run_clicks, show_more_clicks):
    # If no agent data yet, return empty message
    if not stored_data['agents']:
        return html.Div("Run simulation to see agent timelines")
    
    # Handle show more button click
    if ctx.triggered_id == 'show-more-button':
        stored_data['visible_agents'] = min(stored_data['visible_agents'] + 20, len(stored_data['agents']))
    
    # Create HTML table for agent timelines
    return create_agent_timeline_table(stored_data['agents'], stored_data['visible_agents'])

def create_agent_timeline_table(agents, max_agents):
    """Create a table showing agent state changes over time using HTML components"""
    # Limit agents to display
    agents_to_show = agents[:max_agents]
    
    # Determine max events to show (columns)
    max_events = 1
    for agent in agents_to_show:
        max_events = max(max_events, len(agent.state_history))
    
    # Limit max events to 10 for display purposes
    max_display_events = min(max_events, 10)
    
    # Create table header
    header = html.Tr([html.Th("Agent ID")] + [html.Th(f"Event {i+1}") for i in range(max_display_events)])
    
    # Create table rows
    rows = []
    for agent in agents_to_show:
        cells = [html.Td(f"Agent {agent.id}")]
        
        for i in range(max_display_events):
            if i < len(agent.state_history):
                state = agent.state_history[i]
                cell_style = {
                    'backgroundColor': COLOR_MAP.get(state, '#ffffff'),
                    'color': 'white',
                    'textAlign': 'center',
                    'padding': '8px'
                }
                cells.append(html.Td(state, style=cell_style))
            else:
                cells.append(html.Td("", style={'padding': '8px'}))
        
        rows.append(html.Tr(cells))
    
    # Create the complete table
    table = html.Table(
        [html.Thead(header), html.Tbody(rows)],
        style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'marginTop': '20px',
            'marginBottom': '20px'
        }
    )
    
    return table

def create_state_figure(positions, infected, immunity, agent_ids, title):
    """Create a scatter plot showing the current state of agents."""
    fig = go.Figure()
    
    # Convert to numpy arrays
    positions_np = np.array(positions)
    infected_np = np.array(infected)
    immunity_np = np.array(immunity)
    
    # Extract positions for each agent type
    infected_pos = positions_np[infected_np]
    infected_ids = [agent_ids[i] for i, inf in enumerate(infected_np) if inf]
    
    immune_pos = positions_np[immunity_np]
    immune_ids = [agent_ids[i] for i, imm in enumerate(immunity_np) if imm]
    
    healthy_pos = positions_np[~infected_np & ~immunity_np]
    healthy_ids = [agent_ids[i] for i, (inf, imm) in enumerate(zip(infected_np, immunity_np)) if not inf and not imm]
    
    # Add scatter traces for each agent type
    if len(infected_pos) > 0:
        hover_texts = [f"Agent {id}" for id in infected_ids]
        fig.add_trace(go.Scatter(
            x=infected_pos[:, 0], y=infected_pos[:, 1], 
            mode='markers', name='Infected',
            marker=dict(color='red', size=10),
            text=hover_texts,
            hoverinfo='text'
        ))
    
    if len(immune_pos) > 0:
        hover_texts = [f"Agent {id}" for id in immune_ids]
        fig.add_trace(go.Scatter(
            x=immune_pos[:, 0], y=immune_pos[:, 1], 
            mode='markers', name='Immune',
            marker=dict(color='blue', size=10),
            text=hover_texts,
            hoverinfo='text'
        ))
    
    if len(healthy_pos) > 0:
        hover_texts = [f"Agent {id}" for id in healthy_ids]
        fig.add_trace(go.Scatter(
            x=healthy_pos[:, 0], y=healthy_pos[:, 1], 
            mode='markers', name='Healthy',
            marker=dict(color='green', size=10),
            text=hover_texts,
            hoverinfo='text'
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis=dict(range=[0, 500], showticklabels=False), 
        yaxis=dict(range=[0, 500], showticklabels=False),
        height=600,
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(font=dict(size=14))
    )
    
    return fig

def create_progression_figure(statistics):
    """Create a line chart showing disease progression over time."""
    infected, immune, healthy = zip(*statistics)
    
    fig = go.Figure()
    
    # Add traces for each agent status
    fig.add_trace(go.Scatter(
        x=list(range(len(statistics))), y=infected, 
        mode='lines', name='Infected',
        line=dict(color='red', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(len(statistics))), y=immune, 
        mode='lines', name='Immune',
        line=dict(color='blue', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(len(statistics))), y=healthy, 
        mode='lines', name='Healthy',
        line=dict(color='green', width=3)
    ))
    
    # Update layout
    fig.update_layout(
        title=dict(text="Disease Progression Over Time", font=dict(size=18)),
        xaxis=dict(title=dict(text="Timestep", font=dict(size=14))),
        yaxis=dict(title=dict(text="Number of Agents", font=dict(size=14))),
        height=600,
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(font=dict(size=14))
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)