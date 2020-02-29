#!/usr/bin/env python
# coding: utf-8

# This script is a chatbot for collecting trucks information based on user input
# Chatbot configuration is stored in the "chatbot_config.yml" file
# Users Conversations are stored in the 'chatbot.log' file
# The collected Trucks information are stored in table format in the 'Trucks.csv' file

# import libs
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
import string
import inflect
import os
from chatterbot import ChatBot
import logging
import yaml

# function converts an index into ranking str if the corresponding model is not unique
def get_ranking(index, model_amount):
    p = inflect.engine()
    if model_amount == 1:
        return ""
    else:
        return p.number_to_words(p.ordinal(index + 1))

# function returns list of clean text words
def text_process(text):
    no_punc = [c for c in text if c not in string.punctuation]
    no_punc = "".join(no_punc)
    return [
        word
        for word in no_punc.split()
        if word.lower() not in stopwords.words("english")
    ]

# function asks question and handle return
def ask_question(question):
    print(cfg["chatbot_name"] + ": " + question)
    logger.debug(cfg["chatbot_name"] + ": " + question)
    message = input(cfg["user_name"] + ": ")
    logger.debug(cfg["user_name"] + ": " + message)
    return message

# read configuration
with open("chatbot_config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile)

# create logger
logger = logging.getLogger("chatbot")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler("chatbot.log"))

# Create chatbot
bot = ChatBot("Trucks")

# create empty list for trucks information
Trucks_Info = pd.DataFrame(columns=cfg["Questions"].keys()).to_dict(orient="list")

# general questions
User_Name = ask_question(cfg["Questions"]["User_Name"])
Owner = ask_question(cfg["Questions"]["Owner"].format(User_Name))
Company = ask_question(cfg["Questions"]["Company"])
Total_Amount_Of_Trucks = ask_question(cfg["Questions"]["Total_Amount_Of_Trucks"])
Brand_Names = ask_question(cfg["Questions"]["Brand_Names"])

# loop through the brands
for k_brand in range(len(text_process(Brand_Names))):

    # ask how many trucks per Brand, if there is more than 1 brand
    if len(text_process(Brand_Names)) != 1:
        Brand_Amount_Of_Trucks = ask_question(
            cfg["Questions"]["Brand_Amount_Of_Trucks"].format(
                text_process(Brand_Names)[k_brand]
            )
        )
    else:
        Brand_Amount_Of_Trucks = Total_Amount_Of_Trucks

    # ask how many models per Brand
    Brand_Amount_Of_Models = ask_question(
        cfg["Questions"]["Brand_Amount_Of_Models"].format(
            text_process(Brand_Names)[k_brand]
        )
    )

    # loop through the models
    for k_model in range(int(Brand_Amount_Of_Models)):

        # ask for the name of each model
        Model_Name = ask_question(
            cfg["Questions"]["Model_Name"].format(
                get_ranking(k_model, int(Brand_Amount_Of_Models)),
                text_process(Brand_Names)[k_brand],
            )
        )

        # ask how many trucks per model, if there is more than 1 model
        if int(Brand_Amount_Of_Models) != 1:
            Model_Amount_Of_Trucks = ask_question(
                cfg["Questions"]["Model_Amount_Of_Trucks"]
            )
        else:
            Model_Amount_Of_Trucks = Brand_Amount_Of_Models

        # ask for the size of each model
        Model_Engine_Size = ask_question(cfg["Questions"]["Model_Engine_Size"])

        # ask for the axles number of each model
        Model_Axles = ask_question(cfg["Questions"]["Model_Axles"])

        # ask for the fuel type of each model
        Model_Fuel = ask_question(cfg["Questions"]["Model_Fuel"])

        # append the Truck model info to the trucks list
        #append general info
        Trucks_Info["User_Name"].append(User_Name)
        Trucks_Info["Owner"].append(Owner)
        Trucks_Info["Company"].append(Company)
        Trucks_Info["Total_Amount_Of_Trucks"].append(Total_Amount_Of_Trucks)
        Trucks_Info["Brand_Names"].append(text_process(Brand_Names)[k_brand])
        #append brand info
        Trucks_Info["Brand_Amount_Of_Trucks"].append(int(Brand_Amount_Of_Trucks))
        Trucks_Info["Brand_Amount_Of_Models"].append(int(Brand_Amount_Of_Models))
        Trucks_Info["Model_Name"].append(Model_Name)
        #append model info
        Trucks_Info["Model_Amount_Of_Trucks"].append(int(Model_Amount_Of_Trucks))
        Trucks_Info["Model_Engine_Size"].append(Model_Engine_Size)
        Trucks_Info["Model_Axles"].append(Model_Axles)
        Trucks_Info["Model_Fuel"].append(Model_Fuel)

# close the conversation
print("Thank you {}, have a nice day!".format(User_Name))
# save the extracted trucks info in the file
Trucks = pd.DataFrame(Trucks_Info)
Trucks.to_csv(
    "Trucks.csv", mode="a", index=False, header=not os.path.isfile("Trucks.csv")
)

