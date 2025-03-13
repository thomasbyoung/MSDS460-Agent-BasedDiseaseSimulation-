# Add this to the beginning of your simulation.py file
# or create a new file with these modifications

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance_matrix

class Agent:
    def __init__(self, agent_id, x, y, infected, resistance, immunity=False, immunityCounter=0, infectedCounter=0, vaccinated=False):
        self.id = agent_id  # Add unique ID
        self.x = x
        self.y = y
        self.infected = infected
        self.resistance = resistance
        self.immunity = immunity
        self.immunityCounter = immunityCounter
        self.infectedCounter = infectedCounter
        self.vaccinated = vaccinated
        # Track state history for this agent
        self.state_history = []
        self.record_state()

    def record_state(self):
        """Record the current state of the agent for history tracking"""
        if self.infected:
            state = 'infected'
        elif self.immunity:
            state = 'immune'
        else:
            state = 'healthy'
        self.state_history.append(state)

    def movement(self, stepSize, xBounds, yBounds):
        self.x += stepSize * np.random.uniform(-1, 1)
        self.y += stepSize * np.random.uniform(-1, 1)
        
        self.x = np.clip(self.x, xBounds[0], xBounds[1])
        self.y = np.clip(self.y, yBounds[0], yBounds[1])
        
        previous_state = 'infected' if self.infected else 'immune' if self.immunity else 'healthy'
        
        if self.infected:
            self.infectedCounter -= 1
            if self.infectedCounter <= 0:
                self.infected = False
                self.immunity = True
                self.immunityCounter = 50
        
        if self.immunity:
            self.immunityCounter -= 1
            if self.immunityCounter <= 0:
                self.immunity = False
        
        # Check if state changed and record if it did
        current_state = 'infected' if self.infected else 'immune' if self.immunity else 'healthy'
        if current_state != previous_state:
            self.record_state()
    
    def infect(self):
        if not self.infected and not self.immunity and not self.vaccinated:
            infectRoll = np.random.uniform()
            if infectRoll > self.resistance:
                self.infected = True
                self.infectedCounter = 50
                self.resistance *= 1.5
                # Record state change when infected
                self.record_state()

    def vaccinate(self):
        if not self.infected:
            self.immunity = True
            self.vaccinated = True
            self.immunityCounter = 100  # Longer immunity for vaccinated agents
            # Record state change when vaccinated
            self.record_state()

# Modified version of runSimulation to track agent states by timestep
def run_simulation_with_tracking(num_agents=500, num_initial_infected=10, resistance=0.3, 
                  step_size=5, bounds=(0, 500), timesteps=500, 
                  proximity=10, vaccination_rate=0.2, vaccination_step=100):
    
    # Initialize agents with IDs
    agents = []
    for i in range(num_agents):
        x = np.random.uniform(bounds[0], bounds[1])
        y = np.random.uniform(bounds[0], bounds[1])
        # Add 1 to i for more human-friendly IDs starting from 1
        agents.append(Agent(i+1, x, y, False, resistance))
    
    # Set initial infected agents
    for i in range(min(num_initial_infected, num_agents)):
        agents[i].infected = True
        agents[i].infectedCounter = 50
        agents[i].record_state()  # Record initial infected state
    
    # Vaccinate agents if specified
    if vaccination_rate > 0:
        num_to_vaccinate = int(len(agents) * vaccination_rate)
        for i in range(num_initial_infected, num_initial_infected + num_to_vaccinate):
            if i < len(agents):
                agents[i].vaccinate()
    
    frames = []
    statistics = []
    agent_states_by_timestep = []
    
    # Run simulation steps
    for i in range(timesteps):
        # Capture state of all agents at this timestep
        timestep_states = {agent.id: 'infected' if agent.infected else 'immune' if agent.immunity else 'healthy' 
                          for agent in agents}
        agent_states_by_timestep.append(timestep_states)
        
        # Vaccinate at specified step if needed
        if i == vaccination_step and vaccination_rate > 0:
            num_to_vaccinate = int(len(agents) * vaccination_rate)
            healthy_agents = [a for a in agents if not a.infected and not a.immunity]
            for agent in healthy_agents[:num_to_vaccinate]:
                agent.vaccinate()
        
        # Move and possibly infect agents
        agents = moveAgents(agents, step_size, bounds, bounds)
        agents = rollInfect(agents, proximity)
        
        # Record data for visualization
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
    
    # Format agent data for the table visualization
    agent_timelines = {}
    for agent in agents:
        agent_timelines[agent.id] = agent.state_history
    
    return frames, statistics, agent_timelines