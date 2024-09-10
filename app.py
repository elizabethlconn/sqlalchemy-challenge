# ------------------------------ IMPORT DEPENDENCIES ------------------------------ # 
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

# ------------------------------ IMPORT FLASK ------------------------------ #
from flask import Flask, jsonify

# ------------------------------ CONNECT ENGINE TO SQLITE ------------------------------ #
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

# ------------------------------ REFLECT DATABASE SCHEMA ------------------------------ #
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()

# ------------------------------ SAVE REFERENCES TO TABLES ------------------------------ #
Measurement = Base.classes.measurement
Station = Base.classes.station

# ------------------------------ CREATE/BIND PYTHON APP & SESSION ------------------------------ #
app_session = Session(engine)
app = Flask(__name__)

# ------------------------------ DISPLAY ALL AVAILABLE ROUTES ON HOMEPAGE ------------------------------ #

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# ------------------------------ PRECIPITATION ROUTE ------------------------------ #

@app.route("/api/v1.0/precipitation")
def precipitation():
    # calculation most recent date and one year ago
    most_recent_date = app_session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    precipitation_data = app_session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago).all()
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

# ------------------------------ STATIONS ROUTE ------------------------------ #

@app.route("/api/v1.0/stations")
def stations():
    results = app_session.query(Station.station).all()
    station_list = list(np.ravel(results))
    return jsonify(station_list)

# ------------------------------ TOBS ROUTE ------------------------------ #

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = app_session.query(Measurement.station, func.count(Measurement.station))\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()[0]
    
    most_recent_date_for_station = app_session.query(func.max(Measurement.date))\
        .filter(Measurement.station == most_active_station).scalar()
    
    one_year_ago_station = dt.datetime.strptime(most_recent_date_for_station, "%Y-%m-%d") - dt.timedelta(days=365)

    tobs_data = app_session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago_station).all()
    
    tobs_list = list(np.ravel(tobs_data))
    return jsonify(tobs_list)


# ------------------------------ START ROUTE ------------------------------ #
@app.route("/api/v1.0/<start>")
def start(start):
    try:
        start_date = datetime.strptime(start,"%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400
    
    start_temp_stats = app_session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date).all()
    
    min_start_temp, avg_start_temp, max_start_temp = start_temp_stats[0]

    start_tobs_dict = {
        "min": min_start_temp,
        "avg": avg_start_temp,
        "max": max_start_temp
    }
    return jsonify(start_tobs_dict)

# ------------------------------ START<>END ROUTE ------------------------------ #
@app.route("/api/v1.0/<start>/<end>")
def range(start,end):
    try:
        start_date = datetime.strptime(start,"%Y-%m-%d")
        end_date = datetime.strptime(end,"%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400
    
    if end_date < start_date:
        return jsonify({"error:" "End date cannot be earlier than start date"}), 400

    tobs_range_stats = app_session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    min_range_temp, avg_range_temp, max_range_temp = tobs_range_stats[0]

    range_tobs_dict = {
        "min": min_range_temp,
        "avg": avg_range_temp,
        "max": max_range_temp
    }

    return jsonify(range_tobs_dict)



if __name__ == "__main__":
    app.run(debug=True)
