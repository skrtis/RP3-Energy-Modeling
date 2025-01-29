import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm


# Variables and Constants
geometric_mean_dust = 3.4 #
geometric_std_dev_dust = 4.7

stavely = (90,2.2)
brooks1 = (57,1.0)
brooks2 = (63,1.5)

def average(a,b,c):
    # convert to m/s from km/h
    a = a * 1000 / 3600
    b = b * 1000 / 3600
    c = c * 1000 / 3600
    return (a+b+c)/3
average = (average(stavely[0],brooks1[0],brooks2[0]),average(stavely[1],brooks1[1],brooks2[1]))

# Equations
def power_transmittance(actual_power,transmittance):
    return actual_power * (1 - transmittance)

def dust_accum_density_perday(particle_size, ND): #deposition velocity 0.20 cm/s and 0.40 cm/s for the PM2.5 and PM2.5-10 
    
    # use particle size to determine deposition velocity
    if particle_size <= 2.5:
       deposition_velocity = 0.13
    if particle_size >= 2.5 and particle_size <= 10:
       deposition_velocity = 0.40
    else:
        deposition_velocity = 0.50 # just asusme mean for long grass

    total_suspended_particles = 39.68 #ug/m^3
    
    return deposition_velocity*total_suspended_particles*(10**-6)*ND*86400

# Log-normal distribution with geometric mean
def dust_rand(geometric_mean, geometric_std):
    return np.random.lognormal(geometric_mean, geometric_std)

def transmittance_gain_windspeed(WS):
    return WS*0.005/100

def transmittance_loss_dust(dust_density):
    return (-0.001335 * dust_density**6 + 0.04398 * dust_density**5 - 
            0.5427 * dust_density**4 + 3.05 * dust_density**3 - 7.703 * dust_density**2 + 
            11.19 * dust_density - 2.25)/100

def wind_rand(mean_wind_speed, std_dev_wind_speed):
    return np.random.gamma(mean_wind_speed, std_dev_wind_speed)

# create a randomized list of 365 booleans from poisson distribution for rainy days
def rain_list(rain_rate):
    rainy_days = np.random.poisson(rain_rate, 365)
    rainy_days = [True if day > 0 else False for day in rainy_days]
    return rainy_days

# create a for loop that will now generate data 
def generate_one_set(rain_rate,actual_power):
    # randomize variables for 365 days
    rain = rain_list(rain_rate)
    total_dust = 0 
    days_row = 0 
    power_perday = []
    wind_perday = []
    # the main for loop which the power output will be calculated from
    for days in rain:
        #provide values for the first day:
        wind_today = wind_rand(average[0],5)
        wind_perday.append(wind_today)

        # generate dust value for the day
        dust_val = dust_rand(geometric_mean_dust, geometric_std_dev_dust)

        if days == True:
            total_dust = total_dust * 0.2
            days_row = 0
        elif days == False and days_row > 0:
            total_dust = dust_accum_density_perday(dust_val,days_row)
        elif days == False and days_row == 0: 
            days_row = 1
            total_dust = dust_accum_density_perday(dust_val, 1)
    
        #store data for each day
        loss = transmittance_loss_dust(total_dust)
        gain = transmittance_gain_windspeed(wind_today)
        transmittance_today = loss-gain 
        if transmittance_today < 0 or transmittance_today > 1:
            transmittance_today = 0
        power_perday.append(power_transmittance(actual_power,transmittance_today))
    
    return power_perday,rain,wind_perday

def write_one_set(power_perday,rain,wind_perday):
    # write the three datasets in a way where 10,000 more sets can be added and reseparated
    with open('dataone.txt', 'a') as f:
        for i in range(365):
            f.write(f'{power_perday[i]},{rain[i]},{wind_perday[i]}\n')
        f.write('--NEWYEAR--\n')

for i in tqdm(range(10000)):
    power_perday,rain,wind_perday = generate_one_set(0.2,465)
    write_one_set(power_perday,rain,wind_perday)
