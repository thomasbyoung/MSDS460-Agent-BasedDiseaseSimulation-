import numpy as np
import matplotlib.pyplot as plt
import imageio.v2 as imageio
from scipy.spatial import distance_matrix
import os
import argparse

class Agent:
    def __init__(self, x, y, infected, resistance, immunity=False, immunityCounter=0, infectedCounter=0, vaccinated=False):
        self.x = x
        self.y = y
        self.infected = infected
        self.resistance = resistance
        self.immunity = immunity
        self.immunityCounter = immunityCounter
        self.infectedCounter = infectedCounter
        self.vaccinated = vaccinated

    def movement(self, stepSize, xBounds, yBounds):
        self.x += stepSize * np.random.uniform(-1, 1)
        self.y += stepSize * np.random.uniform(-1, 1)
        
        self.x = np.clip(self.x, xBounds[0], xBounds[1])
        self.y = np.clip(self.y, yBounds[0], yBounds[1])
        
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
    
    def infect(self):
        if not self.infected and not self.immunity and not self.vaccinated:
            infectRoll = np.random.uniform()
            if infectRoll > self.resistance:
                self.infected = True
                self.infectedCounter = 50
                self.resistance *= 1.5

    def vaccinate(self):
        if not self.infected:
            self.immunity = True
            self.vaccinated = True
            self.immunityCounter = 100  # Longer immunity for vaccinated agents

def vaccinate_agents(agents, vaccination_rate=0.2):
    num_to_vaccinate = int(len(agents) * vaccination_rate)
    selected_agents = np.random.choice(agents, num_to_vaccinate, replace=False)
    for agent in selected_agents:
        agent.vaccinate()

def getPosition(agents):
    positions = []
    for agent in agents:
        positions.append([agent.x, agent.y])
    return np.array(positions)

def moveAgents(agents, stepSize, xBounds, yBounds):
    for agent in agents:
        agent.movement(stepSize, xBounds, yBounds)
    return agents

def getInfected(agents):
    infected = []
    for agent in agents:
        infected.append(agent.infected)
    return infected

def getCloseAgents(distanceMatrix, agentNumber, proximity_threshold=10):
    sort = np.argsort(distanceMatrix[agentNumber])
    closeMask = distanceMatrix[agentNumber][sort] < proximity_threshold
    closeAgents = np.argsort(distanceMatrix[agentNumber])[closeMask][1:]
    return closeAgents

def rollInfect(agents, proximity_threshold=10):
    positions = getPosition(agents)
    distanceMatrix = distance_matrix(positions, positions)
    for i in range(len(agents)):
        closeAgents = getCloseAgents(distanceMatrix, i, proximity_threshold)
        for j in closeAgents:
            if agents[j].infected and not agents[i].immunity:
                agents[i].infect()
    return agents

def trackCounts(agents):
    infected = sum(1 for agent in agents if agent.infected)
    immune = sum(1 for agent in agents if agent.immunity)
    healthy = sum(1 for agent in agents if not agent.infected and not agent.immunity)
    return infected, immune, healthy

def makeGif(frames, name, duration=100):
    os.makedirs("frames", exist_ok=True)
    images = []
    for counter, frame in enumerate(frames):
        plt.figure(figsize=(8, 8))
        plt.scatter(frame[0], frame[1], c=frame[2], cmap="RdYlGn_r")
        plt.title(f"Infected = {np.sum(frame[2])}")
        plt.tick_params(left=False, right=False, labelleft=False, labelbottom=False, bottom=False)
        frame_path = f"frames/{counter}.png"
        plt.savefig(frame_path)
        images.append(imageio.imread(frame_path))
        plt.close()
    imageio.mimsave(name, images, duration=duration)
    print(f"Animation saved as {name}")
    for file in os.listdir("frames"):
        os.remove(os.path.join("frames", file))
    os.rmdir("frames")

def run_simulation(num_agents=500, num_initial_infected=10, resistance=0.3, 
                  step_size=5, bounds=(0, 500), timesteps=500, 
                  proximity=10, vaccination_rate=0.2, vaccination_step=100, 
                  create_gif=True, plot_stats=True):
    agents = [Agent(np.random.uniform(bounds[0], bounds[1]), np.random.uniform(bounds[0], bounds[1]), False, resistance) for _ in range(num_agents)]
    for i in range(min(num_initial_infected, num_agents)):
        agents[i].infected = True
        agents[i].infectedCounter = 50
    vaccinate_agents(agents, vaccination_rate)
    frames = []
    statistics = []
    for i in range(timesteps):
        if i == vaccination_step:
            vaccinate_agents(agents, vaccination_rate)
        agents = moveAgents(agents, step_size, bounds, bounds)
        agents = rollInfect(agents, proximity)
        positions = getPosition(agents)
        infected = getInfected(agents)
        if create_gif:
            frames.append([positions[:, 0], positions[:, 1], infected])
        if plot_stats:
            infected_count, immune_count, healthy_count = trackCounts(agents)
            statistics.append((infected_count, immune_count, healthy_count))
    if create_gif:
        makeGif(frames, "disease_simulation.gif")
    if plot_stats:
        plot_statistics(statistics, "disease_stats.png")
    return agents, statistics
