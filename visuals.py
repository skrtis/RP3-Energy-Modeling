import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

def data_unpacker():
    power_total= []
    rain_total= []
    wind_averages = []
    power_temporary = []
    rain_count = 0
    wind_temporary = []
    with open('dataone.txt') as f:
        for line in f:
            if line.strip() == "--NEWYEAR--":
                power_total.append(power_temporary) 
                rain_total.append(rain_count)
                wind_averages.append(sum(wind_temporary)/len(wind_temporary))
                power_temporary = []
                rain_count = 0
                wind_temporary = []
            else:
                p, r, w = line.split(',')
                power_temporary.append(float(p))
                if r == 'True':
                    rain_count += 1
                wind_temporary.append(float(w))

    return power_total, rain_total, wind_averages

powers, rains, winds  = data_unpacker()

# Calculate daily average power across all years
daily_average_power = np.mean(powers, axis=0)

# Plot each array in powers as a single line
plt.figure(figsize=(12, 8))
for power in tqdm(powers):
    plt.plot(power)
# Plot the daily average power
plt.plot(daily_average_power, 'k--', label='Daily Average Power')
plt.xlabel('Day of the Year')
plt.ylabel('Power Output')
plt.title('Power Output Over the Year for Each Year')
plt.legend()
plt.show()

# Calculate list power averages, of each list in power
power_average = [sum(power)/len(power) for power in powers]

# Create bins
wind_edges = np.linspace(min(winds), max(winds), 10)
rain_edges = np.linspace(min(rains), max(rains), 10)

# Initialize power matrix
power_matrix = np.zeros((len(wind_edges)-1, len(rain_edges)-1))
count_matrix = np.zeros_like(power_matrix)

# Fill power matrix with average power values
for year in range(len(winds)):
    w_idx = np.digitize(winds[year], wind_edges) - 1
    r_idx = np.digitize(rains[year], rain_edges) - 1
    
    if w_idx < len(wind_edges)-1 and r_idx < len(rain_edges)-1:
        power_matrix[w_idx, r_idx] += power_average[year]
        count_matrix[w_idx, r_idx] += 1

# Calculate average power per bin
power_matrix = np.divide(power_matrix, count_matrix, where=count_matrix!=0)

# Get min and max power values from power_average
power_min = min(power_average)
power_max = max(power_average)

# 2D Heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(power_matrix.T, 
            xticklabels=np.round(wind_edges[:-1], 1),
            yticklabels=np.round(rain_edges[:-1], 1),
            cmap='Purples',
            vmin=power_min,
            vmax=power_max)
plt.xlabel('Wind Speed')
plt.ylabel('Rain Days')
plt.title('Average Power Output by Wind Speed and Rain Days')
plt.show()

