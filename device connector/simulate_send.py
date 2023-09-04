import os
from sqlite3 import Timestamp
import sys
import gym
import eplus_env
from itertools import groupby
import argparse
import numpy as np
import pandas as pd
import copy
import pickle
import time
from utils import make_dict
from virtual_devices import simplePublisher as pub
import json
import datetime
 
def main():
    # Create Simulation Environment
    env = gym.make('idf-non-ottimizzato-v0')
    publisher = pub.MyPublisher('Lab-Building')
    publisher.start()
    # Modify here: Outputs from EnergyPlus; Match the variables.cfg file.
    #obs_name = ["T_ext", "Wind_Speed", "Wind_Direction", "DHI", "DNI", "Tin_Kitchen",
    #    "Tin_Bathroom1","Tin_Room1","Tin_Corridor","Tin_Bathroom","Tin_Livingroom","Tin_Room",
    #    "Electricity","DistrictHeating","DistrictCooling","Bath1_shade","Room1_shade1","Room1_shade2","Bath_shade","Living_shade1","Living_shade2","Room_shade1","Room_shade2"]
    obs_name = ["T_ext", "Wind_Speed", "Wind_Direction", "DHI", "DNI", "cos_teta", "AR_Kitchen", "ACR_Kitchen", "Tin_Kitchen",
                "Tin_Stairs", "Tin_Bathroom", "Tin_Storage", "Tin_Bedroom", "Tin_LivingRoom",
                "Electricity","DistrictHeating","DistrictCooling", "Kitchen1_Shade", "Kitchen2_Shade", "Bathroom1_Shade",
                "Bathroom2_Shade", "Bedroom1_Shade", "Bedroom2_Shade", "LivingRoom_Shade"]



    tot_days = 365 # tol_days: Total number of days/episodes; Each episode is a natural day    
    n_step_hour = 2 #timesteps in one hour
    n_step = n_step_hour*24
    timeStep, obser, isTerminal,_ = env.reset()
    start_time = pd.datetime(year = env.start_year, month = env.start_mon, day = env.start_day)
    #start_time = pd.datetime(year = datetime.date.today().year, month = datetime.date.today().month, day = datetime.date.today().day)
    cur_time = start_time
    obs_dict = make_dict(obs_name, obser)
    timeStamp = []
    observations = []
    actions_taken = []
    
    for i_episode in range(tot_days):
        for t in range(n_step):
            
            #Define the actions to take if there are

            
            #Put your actions in a list to pass to the next step
            
            input_actions =[]
            
            #Perform the step
            timeStep, obser, isTerminal,_ = env.step(input_actions)

            cur_time = start_time + pd.Timedelta(seconds = timeStep)
            

            # Save for record
            timeStamp.append(cur_time)
            obs_dict = make_dict(obs_name, obser)
            print(obs_dict)
            observations.append(obser)
            if len(input_actions)>0:
                actions_taken.append([input_actions])

            #send the data
            for key,val in obs_dict.items():

                payload={
                        "location":"MyBuilding",
                        "measurement":key,
                        "node":key,
                        #"tags"
                        "time_stamp":str(cur_time),
                        "value":val}
                publisher.myPublish("/ict4bd/"+str(key),json.dumps(payload))

                time.sleep(0.01)
            print("inviato",payload)
            time.sleep(1)

    env.end_env()
if __name__ == '__main__':
    main()
