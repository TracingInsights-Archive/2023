import json
import os

import fastf1
import numpy as np
import pandas as pd
import requests
import utils

YEAR = 2023


events = [
    "Qatar Grand Prix",
    "Pre-Season Testing",
    "Bahrain Grand Prix",
    "Saudi Arabian Grand Prix",
    "Australian Grand Prix",
    "Azerbaijan Grand Prix",
    "Miami Grand Prix",
    "Monaco Grand Prix",
    "Spanish Grand Prix",
    "Canadian Grand Prix",
    "Austrian Grand Prix",
    "British Grand Prix",
    "Hungarian Grand Prix",
    "Belgian Grand Prix",
    "Dutch Grand Prix",
    "Italian Grand Prix",
    "Singapore Grand Prix",
    "United States Grand Prix",
    "Mexico City Grand Prix",
    "São Paulo Grand Prix",
    "Las Vegas Grand Prix",
    "Abu Dhabi Grand Prix",
    "Japanese Grand Prix",
]


def sessions_available(year: int, event: str | int) -> any:
    # get sessions available for a given year and event
    event = str(event)
    data = utils.LatestData(year)
    sessions = data.get_sessions(event)
    return sessions


def fastest_lap(year: int, event: str | int, session: str) -> any:
    f1session = fastf1.get_session(year, event, session)
    f1session.load(telemetry=False, weather=False, messages=False)
    laps = f1session.laps

    drivers = pd.unique(laps["Driver"])

    list_fastest_laps = list()

    for drv in drivers:
        drvs_fastest_lap = laps.pick_driver(drv).pick_fastest()
        list_fastest_laps.append(drvs_fastest_lap)

    df = (
        fastf1.core.Laps(list_fastest_laps)
        .sort_values(by="LapTime")
        .reset_index(drop=True)
    )

    pole_lap = df.pick_fastest()
    df["Diff"] = df["LapTime"] - pole_lap["LapTime"]

    # car_colors = utils.team_colors(year)

    # df["fill"] = df["Team"].map(car_colors)

    # convert timedelta to float and round to 3 decimal places
    df["Diff"] = df["Diff"].dt.total_seconds().round(3)
    df["LapTime"] = df["LapTime"].dt.total_seconds().round(3)
    df = df[
        [
            "Driver",
            "LapTime",
            "Diff",
            "Team",
        ]
    ]

    # remove nan values in any column
    df = df.dropna()

    df_json = df.to_dict("records")

    return {"fastest": df_json}


# Your list of events
events_list = events

# Loop through each event
for event in events_list:
    sessions = sessions_available(YEAR, event)
    if event == "Qatar Grand Prix":
        sessions = [
            "Practice 1",
            "Qualifying",
            "Sprint Shootout",
            "Sprint",
            "Race",
        ]

    for session in sessions:
        fastest_lap_dict = fastest_lap(YEAR, event, session)

        # Specify the file path where you want to save the JSON data
        file_path = f"{event}/{session}/fastest_lap.json"

        # Save the dictionary to a JSON file
        with open(file_path, "w") as json_file:
            json.dump(fastest_lap_dict, json_file)

        print(f"Dictionary saved to {file_path}")
