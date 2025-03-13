import numpy as np
import os
import imageio
import matplotlib.pyplot as plt
from scipy.spatial import distance_matrix

class Agent():
    def __init__(self, x, y, infected, resistance, immunity=False, immunityCounter=0, infectedCounter=0):
        self.x = x
        self.y = y
        self.infected = infected
        self.resistance = resistance
        self.immunity = immunity
        self.immunityCounter = immunityCounter
        self.infectedCounter = infectedCounter

    def movement(self, stepSize, xBounds, yBounds):
        self.x += stepSize * np.random.uniform(-1, 1)
        self.y += stepSize * np.random.uniform(-1, 1)

        if self.x < xBounds[0]:
            self.x = xBounds[0]
        elif self.x > xBounds[1]:
            self.x = xBounds[1]

        if self.y < yBounds[0]:
            self.y = yBounds[0]
        elif self.y > yBounds[1]:
            self.y = yBounds[1]

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
        if not self.infected and not self.immunity:
            infectRoll = np.random.uniform()
            if infectRoll > self.resistance:
                self.infected = True
                self.infectedCounter = 50
                self.resistance *= 1.5

def getPosition(agents):
    positions = np.array([[agent.x, agent.y] for agent in agents])
    return positions

def moveAgents(agents, stepSize, xBounds, yBounds):
    for agent in agents:
        agent.movement(stepSize, xBounds, yBounds)
    return agents

def getInfected(agents):
    return [agent.infected for agent in agents]

def getCloseAgents(distanceMatrix, agentNumber):
    sort = np.argsort(distanceMatrix[agentNumber])
    closeMask = distanceMatrix[agentNumber][sort] < 10
    closeAgents = np.argsort(distanceMatrix[agentNumber])[closeMask][1:]
    return closeAgents

def rollInfect(agents):
    positions = getPosition(agents)
    distanceMatrix = distance_matrix(positions, positions)

    for i in range(len(agents)):
        closeAgents = getCloseAgents(distanceMatrix, i)
        for j in closeAgents:
            if agents[j].infected and not agents[i].immunity:
                agents[i].infect()
    return agents

def trackCounts(agents):
    infected = sum(agent.infected for agent in agents)
    immune = sum(agent.immunity for agent in agents)
    healthy = sum(not agent.infected and not agent.immunity for agent in agents)
    return infected, immune, healthy

def makeGif(frames, name):
    os.makedirs("frames", exist_ok=True)
    images = []
    for counter, frame in enumerate(frames):
        plt.figure(figsize=(6,6))
        plt.scatter(frame[0], frame[1], c=frame[2], cmap="RdYlGn_r")
        plt.title("Infected = " + str(np.sum(frame[2])))
        plt.tick_params(left=False, right=False, labelleft=False, labelbottom=False, bottom=False)
        frame_path = f"frames/{counter}.png"
        plt.savefig(frame_path)
        images.append(imageio.imread(frame_path))
        plt.close()
    imageio.mimsave(name, images, duration=200)
    for file in os.listdir("frames"):
        os.remove(os.path.join("frames", file))
    os.rmdir("frames")

def vaccinate_agents(agents, vaccination_rate=0.3):
    """
    Vaccinates a percentage of the population by granting them immunity.

    Parameters:
    agents (list): List of agent objects.
    vaccination_rate (float): Fraction of healthy agents to vaccinate.
    """
    healthy_agents = [agent for agent in agents if not agent.infected and not agent.immunity]
    num_to_vaccinate = int(len(healthy_agents) * vaccination_rate)

    vaccinated_agents = np.random.choice(healthy_agents, num_to_vaccinate, replace=False)

    for agent in vaccinated_agents:
        agent.immunity = True
        agent.immunityCounter = 100  # Vaccination grants longer immunity counter

    return agents
  
agents = []
for _ in range(500):
    x = np.random.uniform(0,500)
    y = np.random.uniform(0,500)
    agents.append(Agent(x, y, 0, .3))

for i in range(10):
    agents[i].infected = True
    agents[i].infectedCounter = 50

stepSize = 5
xBounds = [0,500]
yBounds = [0,500]

frames = []
for i in range(500):
    if i % 100 == 0:  # Apply vaccination every 100 steps
        agents = vaccinate_agents(agents, vaccination_rate=0.3)
    agents = moveAgents(agents, stepSize, xBounds, yBounds)
    agents = rollInfect(agents)
    positions = getPosition(agents)
    infected = getInfected(agents)
    frames.append([positions[:,0], positions[:,1], infected])

makeGif(frames, "Vaccine_simulation.gif")
