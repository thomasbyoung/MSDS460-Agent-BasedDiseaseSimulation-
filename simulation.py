import numpy as np
import matplotlib.pyplot as plt
import imageio.v2 as imageio
from scipy.spatial import distance_matrix
import os
import argparse

class Agent:
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



    infected, immune, healthy = zip(*statistics)
    
    plt.figure(figsize=(10, 6))
    plt.plot(infected, 'r-', label='Infected')
    plt.plot(immune, 'b-', label='Immune')
    plt.plot(healthy, 'g-', label='Healthy')
    
    plt.xlabel('Time Step')
    plt.ylabel('Number of Agents')
    plt.title('Disease Progression Over Time')
    plt.legend()
    plt.grid(True)
    
    if output_file:
        plt.savefig(output_file)
        print(f"Statistics plot saved as {output_file}")
    else:
        plt.show()


def run_simulation(num_agents=500, num_initial_infected=10, resistance=0.3, 
                  step_size=5, bounds=(0, 500), timesteps=500, 
                  proximity=10, create_gif=True, plot_stats=True):

    print(f"Starting simulation with {num_agents} agents, {num_initial_infected} initially infected")
    print(f"Agent resistance: {resistance}, Proximity threshold: {proximity}")
    
    agents = []
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
        if i % 50 == 0:
            print(f"Processing step {i}/{timesteps}")
        
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


def main():
    parser = argparse.ArgumentParser(description='Run a disease spread simulation')
    
    parser.add_argument('--agents', type=int, default=500,
                        help='Number of agents in the simulation')
    parser.add_argument('--infected', type=int, default=10,
                        help='Number of initially infected agents')
    parser.add_argument('--resistance', type=float, default=0.3,
                        help='Base resistance of agents to infection (0-1)')
    parser.add_argument('--step', type=float, default=5,
                        help='Step size for agent movement')
    parser.add_argument('--size', type=int, default=500,
                        help='Size of the simulation area (square)')
    parser.add_argument('--timesteps', type=int, default=500,
                        help='Number of simulation steps')
    parser.add_argument('--proximity', type=float, default=10,
                        help='Distance threshold for infection spread')
    parser.add_argument('--no-gif', action='store_true',
                        help='Skip creating the animation GIF')
    parser.add_argument('--no-plot', action='store_true',
                        help='Skip creating the statistics plot')
    
    args = parser.parse_args()
    
    run_simulation(
        num_agents=args.agents,
        num_initial_infected=args.infected,
        resistance=args.resistance,
        step_size=args.step,
        bounds=(0, args.size),
        timesteps=args.timesteps,
        proximity=args.proximity,
        create_gif=not args.no_gif,
        plot_stats=not args.no_plot
    )


if __name__ == "__main__":
    main()