import random
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION AND MODEL PARAMETERS ---

# The number of simulation steps to run, where each step is one year
NUM_STEPS = 50

# The number of simulated households per sub-market
INITIAL_HOUSEHOLDS_PER_SUBMARKET = 500

# The probability that a household with a home will put it up for sale each year
SELL_PROBABILITY = 0.15 

# Sub-market definitions and their characteristics
SUBMARKETS = {
    "Downtown": {
        "house_value_range": (50000, 150000),
        "income_range": (30000, 70000),
        "price_drop_rate": 0.05,  # Individual sellers drop price by 5%
        "bank_drop_rate": 0.15,   # Banks drop price by 15%
    },
    "City_Suburban": {
        "house_value_range": (100000, 300000),
        "income_range": (50000, 120000),
        "price_drop_rate": 0.03,
        "bank_drop_rate": 0.10,
    },
    "Far_Suburban": {
        "house_value_range": (200000, 600000),
        "income_range": (80000, 200000),
        "price_drop_rate": 0.01,
        "bank_drop_rate": 0.05,
    }
}

# --- 2. AGENT CLASSES ---

class Household:
    """Represents a household agent with specific financial characteristics."""
    def __init__(self, submarket):
        self.submarket = submarket
        # Use random.choices for weighted selection, more buyers than sellers
        self.is_buyer = random.choices([True, False], weights=[0.4, 0.6])[0]
        self.years_as_buyer = 0
        self.income = random.uniform(*SUBMARKETS[submarket]["income_range"])
        self.house_budget = self.income * random.uniform(2.5, 4.0) # A common rule of thumb for home affordability
        self.owned_house = None # A reference to the House object this household owns

    def act(self, listings):
        """Main action method for the household."""
        if self.is_buyer:
            # Act as a buyer
            if self.years_as_buyer > 4:
                # Leave the system if unable to find a home after 4 years
                return "leave", None
            
            # Find listings within budget from their submarket and other submarkets
            affordable_listings = [
                h for h in listings if h.current_price <= self.house_budget
            ]

            if affordable_listings:
                # Simple logic: bid on a random affordable house
                target_house = random.choice(affordable_listings)
                return "buy", target_house
            else:
                self.years_as_buyer += 1
                return "wait", None
        else:
            # Act as a seller (if they own a house to sell)
            if self.owned_house and random.random() < SELL_PROBABILITY:
                # Seller decides to list their house for sale
                self.owned_house.is_for_sale = True
                return "sell", self.owned_house
            
            return "stay", None

class House:
    """Represents a single house in the simulation."""
    def __init__(self, submarket):
        self.submarket = submarket
        self.original_price = random.uniform(*SUBMARKETS[submarket]["house_value_range"])
        self.current_price = self.original_price
        self.is_for_sale = False
        self.is_bank_owned = False
        self.owner = None

# --- 3. THE SIMULATION ENVIRONMENT ---

class CityModel:
    """Manages the simulation environment, agents, and market dynamics."""
    def __init__(self):
        self.households = []
        self.houses = []
        self.buyer_to_seller_ratio = 1.0 # D-S Ratio
        self.year = 0

        # Initialize households and houses for each submarket
        for submarket_name, _ in SUBMARKETS.items():
            for _ in range(INITIAL_HOUSEHOLDS_PER_SUBMARKET):
                new_household = Household(submarket_name)
                self.households.append(new_household)
                
                # Each household starts by owning a house
                new_house = House(submarket_name)
                new_house.owner = new_household
                new_household.owned_house = new_house
                self.houses.append(new_house)

        # Store history for analysis. Changed keys to match SUBMARKETS capitalization.
        self.history = {
            "total_households": [len(self.households)],
            "total_houses": [len(self.houses)],
            "bank_owned_houses": [0],
            "median_price_Downtown": [0],
            "median_price_City_Suburban": [0],
            "median_price_Far_Suburban": [0],
        }
        
    def run_step(self):
        """Executes one year of the simulation."""
        self.year += 1
        
        # Lists to track changes
        newly_bank_owned = []
        newly_sold_houses = []
        
        # Price depreciation for unsold and bank-owned houses
        for house in self.houses:
            if house.is_for_sale:
                # Reduce price if it's been on the market
                if house.is_bank_owned:
                    house.current_price *= (1 - SUBMARKETS[house.submarket]["bank_drop_rate"])
                else:
                    house.current_price *= (1 - SUBMARKETS[house.submarket]["price_drop_rate"])
        
        # Phase 1: Households act (buy/sell/leave)
        for household in list(self.households):
            action, target = household.act(self.houses)
            
            if action == "buy" and target:
                # Transaction occurs
                if target.owner:
                    # Seller's house is sold
                    target.owner.owned_house = None
                    target.owner.is_buyer = False
                
                # Update ownership
                target.owner = household
                household.owned_house = target
                household.is_buyer = False
                household.years_as_buyer = 0
                target.is_for_sale = False
                newly_sold_houses.append(target)
            
            elif action == "leave":
                # Household leaves the system
                if household.owned_house:
                    household.owned_house.is_for_sale = True
                    household.owned_house.is_bank_owned = False # It becomes a regular listing first
                    household.owned_house.owner = None
                self.households.remove(household)
            
            elif action == "sell" and target:
                # The act method has already set the is_for_sale flag
                pass # The house is now a listing

        # Phase 2: Update unsold homes
        for house in self.houses:
            # If a house was listed for sale and wasn't sold, it becomes bank-owned
            if house.is_for_sale and house not in newly_sold_houses:
                house.is_bank_owned = True
                newly_bank_owned.append(house)
                
        # Phase 3: Recalculate and record metrics
        self._record_metrics()
        
    def _record_metrics(self):
        """Calculates and stores key metrics for the current step."""
        self.history["total_households"].append(len(self.households))
        self.history["total_houses"].append(len(self.houses))
        self.history["bank_owned_houses"].append(
            len([h for h in self.houses if h.is_bank_owned])
        )
        
        for submarket_name in SUBMARKETS.keys():
            submarket_prices = [
                h.current_price for h in self.houses if h.submarket == submarket_name
            ]
            if submarket_prices:
                median_price = sorted(submarket_prices)[len(submarket_prices) // 2]
                self.history[f"median_price_{submarket_name}"].append(median_price)
            else:
                self.history[f"median_price_{submarket_name}"].append(0)

    def run_simulation(self):
        """Runs the main simulation loop and plots results."""
        for step in range(NUM_STEPS):
            self.run_step()
            print(f"Year {self.year}: Households = {len(self.households)}, "
                  f"Bank-owned homes = {self.history['bank_owned_houses'][-1]}")
        
        self.plot_results()

    def plot_results(self):
        """Plots the population and price trends over time."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

        # Plot 1: Population and Bank-Owned Homes
        ax1.plot(self.history["total_households"], label="Total Households", color="blue")
        ax1.plot(self.history["bank_owned_houses"], label="Bank-Owned Homes", color="red")
        ax1.set_title("Population & Bank-Owned Home Trends")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Count")
        ax1.legend()
        ax1.grid(True)

        # Plot 2: Median House Prices by Submarket
        ax2.plot(self.history["median_price_Downtown"], label="Downtown", color="darkred")
        ax2.plot(self.history["median_price_City_Suburban"], label="City Suburban", color="orange")
        ax2.plot(self.history["median_price_Far_Suburban"], label="Far Suburban", color="green")
        ax2.set_title("Median House Price by Submarket")
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Median Price ($)")
        ax2.legend()
        ax2.grid(True)

        plt.tight_layout()
        plt.show()

# --- 4. RUN THE SIMULATION ---

if __name__ == "__main__":
    model = CityModel()
    model.run_simulation()
