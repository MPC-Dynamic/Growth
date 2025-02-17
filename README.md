# Buildout, Resident Turnover and Household Satisfaction

### Forecast

Step 1: Forecast state transition probabilities from the historical set:
Run "[Forecast Transition Probabilities](https://github.com/MPC-Dynamic/Growth/blob/main/Forecast%20Transition%20Probabilities.ipynb)" on historical_transition_probabilities.csv -> forcasted_transition_probabilities_0.15.xlsx   


Step 2: Generate the annual permits forecast based on the current state and forecasted state transition probabilities:
Run "[Forecast Annual Permits](https://github.com/MPC-Dynamic/Growth/blob/main/Forecast%20Annual%20Permits.ipynb)" on forcasted_transition_probabilities_0.15.xlsx  


[Extract property data ](https://github.com/MPC-Dynamic/Growth/blob/main/extract_property_data.py)

[historical transition probabilities](https://github.com/MPC-Dynamic/Growth/blob/main/historical_transition_probabilities.csv)

[Find peaks and throughs](https://github.com/MPC-Dynamic/Growth/blob/main/BoomsBusts.py) in housing data

[Plot custom vs all homes](https://github.com/MPC-Dynamic/Growth/blob/main/custom-homes.py) inclusing spec homes

[early sales histograms](https://github.com/MPC-Dynamic/Growth/blob/main/YearlySales.py)


# Median tenure and Structural Changes in Resident Turnover

[Kaplan Meier estimates](https://github.com/MPC-Dynamic/Growth/blob/main/Tenure.py) of median tenure and [critical years](https://github.com/MPC-Dynamic/Growth/blob/main/tenureHazards.py)

[Rolling averages in tenure trends](https://github.com/MPC-Dynamic/Growth/blob/main/simple_tenure_trends.py)

[Fit Weibull curves](https://github.com/MPC-Dynamic/Growth/blob/main/Weibulls.py)


# Satisfaction 

[ANOVA and Tukey HSD tests](https://github.com/MPC-Dynamic/Growth/blob/main/Tukey.py)

[Kruskal-Wallis and Mann-Whitney tests](https://github.com/MPC-Dynamic/Growth/blob/main/Tukey.py)

[Ploting generational differences](https://github.com/MPC-Dynamic/Growth/blob/main/generations.py)

###
[OSF DATA](https://osf.io/tgv6q/)
