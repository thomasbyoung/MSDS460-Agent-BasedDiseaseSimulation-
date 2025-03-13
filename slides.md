---
marp: true
theme: gaia
---

# MSDS 460 Final Project: Agent-Based Disease Simulation


**Group Members:**
<div style="font-size: smaller;">
Albert Lee<br>
Alberto Olea<br>
Maddie Stapulionis<br>
Migus Wong<br>
Thomas Young
</div>

<!-- Add the photo to the bottom right -->
![bottom right](/slideImages/CovImg.jpg)
<style scoped>
img[alt="bottom right"] {
  position: absolute;
  bottom: 10px;
  right: 10px;
  width: 500px; /* Adjust the size as needed */
}
</style>
---
# Agenda
## 1. Project Overview & History
## 2. Simulation Design
## 3. Insights & Findings
##  4. Future Dirction & Conclusion

---

# Simulating the Spread of Disease
**Objective:** Be able to simulate the spread of a disease within a closed community under different scenarios.

**Goals:** Understand how disease characteristics and aspects of a population affect a population outcome.

**Methodology:** Use Python to create an agent-based simulation and create a dashboard of interactivity.

---

<style scoped>
img[alt="bottom right"] {
  position: absolute;
  bottom: 10px;
  right: 10px;
  width: 400px; /* Adjust the size as needed */
}
</style>

## Historical/Industry Context 
 - **Epidemiology** is the study and analysis of the distribution, patterns and determinants of health and disease conditions in a defined population, and application of this knowledge to prevent diseases.
 - First recorded use of statistics in this field was in 1662 with the great plague Invention of computers in the 1950s allowed for more complex simulations to happen involving more variables 
 - Utilized extensively during COVID-19 pandemic for forecasting infection and death rates.

---
# Objective

1. ## Simulate disease spread using an agent-based model.

2. ## Understand effects of vaccination, isolation, and transmission likelihood.

3. ## Inform policies for future pandemic responses.

---


## Models each individual separately (agents).

## Captures variability in behavior and outcomes.

---
# Agent Statuses

| Status    | Description |
|-----------|-------------|
| **Uninfected** | The agent does not currently have the disease but can get it. |
| **Infected**   | The agent has the disease.  |
| **Immune**     | These agents have been infected but their infection counter has expired. They are immune for a determined number of events meaning they cannot spread the disease. |

---
# Adjustable Parameters

**Number of Agents**
This represents the total starting number of agents being simulated. As the total number of agents increases, the likelihood of agents making contact with each other increases. As a result, this variable can be directly related to the population density of the environment.
**Immunity Duration**
This can be thought of agents who are unable to be infected with the disease meaning they are neither able to spread or contract the disease during this time. 

---
**Infection Duration**
Infection duration represents how long an agent is marked as infected and can infect other uninfected agents. 
**Agent Vaccination**
This variable is included throughout the runtime of the model to simulate the effect of a vaccination campaign that grants immunity to a designated fraction of healthy agents. A higher immunity duration counter of 100 is granted to vaccinated agents

---
**Resistance Probability and Reinfection Resistance Factor**
Both of these variables determine the likelihood of an agent being infected if they are placed in contact with each other. Similar to how antibodies often adapt to better fight known diseases once it's been introduced, the reinfection resistance factor represents and increased likelihood of resisting infection each time the agent has seen the virus.


---
# Simulation Demo

---
# Insights and Future Direction
* Simulation demonstrates how the effect of a disease on a population
* Opportunities for improvement: Fatality Rates; individualized factors, non-random movement, effects isolation effects.
* Practical Value: Opportunities for policy creation; disease research
