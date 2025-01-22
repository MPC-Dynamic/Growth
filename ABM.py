import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------
# Simulation Parameters
# ------------------------------------------------------------------------------
NUM_YEARS = 50           # Number of time steps to simulate (e.g., years)
INITIAL_POP = 100        # Initial number of residents
MAX_POP = 1000           # Arbitrary cap to avoid unbounded growth in this example

# Community-level parameters (you can make these change over time if needed)
BASE_COST_OF_LIVING = 0.3
BASE_AMENITY_FACTOR = 0.7

# Satisfaction update weights
SATISFACTION_WEIGHT_AMENITY = 0.6
SATISFACTION_WEIGHT_COST    = 0.4

# Probability thresholds
MOVE_OUT_SAT_THRESHOLD = 0.4  # If satisfaction drops below this, high chance to move out
MOVE_OUT_BASE_PROB = 0.05     # Base probability of moving out each year (for random turnover)

# Arrival rates
ARRIVALS_MEAN = 5  # Average number of new arrivals per year (Poisson distributed for realism)

# ------------------------------------------------------------------------------
# Agent Definition
# ------------------------------------------------------------------------------
class Resident:
    def __init__(self, 
                 resident_id,
                 satisfaction, 
                 price_sensitivity,
                 years_in_community=0):
        """
        :param resident_id: Unique identifier for the resident
        :param satisfaction: Current satisfaction level [0, 1]
        :param price_sensitivity: How strongly cost affects this resident's satisfaction [0, 1]
        :param years_in_community: How many years the resident has lived in the community
        """
        self.id = resident_id
        self.satisfaction = satisfaction
        self.price_sensitivity = price_sensitivity
        self.years_in_community = years_in_community
    
    def update_satisfaction(self, amenity_factor, cost_of_living):
        """
        Update satisfaction based on current amenity factor, cost of living, 
        and the agent's price sensitivity.
        """
        amenity_contribution = SATISFACTION_WEIGHT_AMENITY * amenity_factor
        cost_contribution = SATISFACTION_WEIGHT_COST * (1 - self.price_sensitivity) - \
                            SATISFACTION_WEIGHT_COST * cost_of_living * self.price_sensitivity
        
        # Simple linear update model
        new_satisfaction = self.satisfaction + amenity_contribution + cost_contribution
        
        # Keep satisfaction within [0, 1]
        self.satisfaction = min(max(new_satisfaction, 0.0), 1.0)
        
    def consider_moving_out(self):
        """
        Returns True if the resident decides to move out.
        This decision is based on:
         1. Low satisfaction,
         2. A random component representing life changes.
        """
        # Higher probability to move out if satisfaction is below threshold
        if self.satisfaction < MOVE_OUT_SAT_THRESHOLD:
            # Probability of moving out can be scaled by how low the satisfaction is
            prob = MOVE_OUT_BASE_PROB + (MOVE_OUT_SAT_THRESHOLD - self.satisfaction)
        else:
            prob = MOVE_OUT_BASE_PROB

        return np.random.rand() < prob
    
    def increment_year(self):
        """
        Called at the end of each time step to increment the resident's tenure.
        """
        self.years_in_community += 1

# ------------------------------------------------------------------------------
# Initialize the Simulation
# ------------------------------------------------------------------------------
np.random.seed(42)  # For reproducibility (optional)

# Create initial population
residents = []
for i in range(INITIAL_POP):
    # Random initial satisfaction between 0.6 and 0.9
    satisfaction = np.random.uniform(0.6, 0.9)
    # Random price sensitivity between 0.2 and 0.8
    price_sens = np.random.uniform(0.2, 0.8)
    
    residents.append(Resident(resident_id=i,
                              satisfaction=satisfaction,
                              price_sensitivity=price_sens))

# For tracking results over time
pop_size_over_time = []
avg_satisfaction_over_time = []

# ------------------------------------------------------------------------------
# Run the Simulation
# ------------------------------------------------------------------------------
for year in range(NUM_YEARS):
    # Shuffle the list so update order doesn't systematically bias results
    np.random.shuffle(residents)

    # 1. Update satisfaction for each resident
    for res in residents:
        res.update_satisfaction(BASE_AMENITY_FACTOR, BASE_COST_OF_LIVING)
    
    # 2. Decide who moves out
    remaining_residents = []
    for res in residents:
        if not res.consider_moving_out():
            remaining_residents.append(res)
    
    residents = remaining_residents
    
    # 3. Add new arrivals (Poisson-distributed)
    num_new_arrivals = np.random.poisson(ARRIVALS_MEAN)
    for _ in range(num_new_arrivals):
        if len(residents) < MAX_POP:
            new_satisfaction = np.random.uniform(0.5, 0.9)
            new_price_sens   = np.random.uniform(0.2, 0.8)
            new_id = np.random.randint(1000000)  # Arbitrary unique ID
            residents.append(Resident(new_id, new_satisfaction, new_price_sens))
    
    # 4. Increment each resident's year counter
    for res in residents:
        res.increment_year()
    
    # 5. Record population stats
    pop_size_over_time.append(len(residents))
    if len(residents) > 0:
        avg_satisfaction_over_time.append(
            np.mean([res.satisfaction for res in residents])
        )
    else:
        avg_satisfaction_over_time.append(0.0)

# ------------------------------------------------------------------------------
# Results Visualization
# ------------------------------------------------------------------------------
years = range(NUM_YEARS)
plt.figure(figsize=(10, 5))

# Plot population over time
plt.subplot(1, 2, 1)
plt.plot(years, pop_size_over_time, marker='o')
plt.title("Population Size Over Time")
plt.xlabel("Year")
plt.ylabel("Number of Residents")

# Plot average satisfaction over time
plt.subplot(1, 2, 2)
plt.plot(years, avg_satisfaction_over_time, color='orange', marker='o')
plt.title("Average Satisfaction Over Time")
plt.xlabel("Year")
plt.ylabel("Satisfaction (0-1)")

plt.tight_layout()
plt.show()

# ------------------------------------------------------------------------------
# End of Simulation
# ------------------------------------------------------------------------------
