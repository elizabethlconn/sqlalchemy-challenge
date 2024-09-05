# Import the dependencies.
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from sqlalchemy import func, Date, cast, Integer

import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime, timedelta

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()


# reflect an existing database into a new model

# reflect the tables


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return "Welcome to my 'Home' page!"

app.run()



#### add my endpoints where it says return above "welcome to my home page"