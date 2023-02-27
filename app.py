import numpy as np
import datetime as dt

from flask import Flask, jsonify, render_template,make_response

import json

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# Initalize Flask
app = Flask(__name__)

# Create a db engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# auto-map
Base = automap_base()
Base.prepare(engine, reflect=True)

# Get the reference to the measurement data and Save the reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Get the highest date record from the mesurement table and walk back 366 days from that record to
# get a years worth of data records
def compute_latest_date():
    year_latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_value= dt.datetime.strptime(year_latest.date, "%Y-%m-%d") - dt.timedelta(days=366)
    return date_value

# Return Precipitation for last 12 months in JSON format
@app.route("/api/v1.0/precipitation")
def precipitation():
    #compute date value and get precp records and convert them into json
    date_value = compute_latest_date()
    precp_records = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_value).all()
    precp_dict = dict(precp_records)
    return jsonify(precp_dict)

# Return Station data in Json
@app.route("/api/v1.0/stations")
def stations():
    #Get Station list and convert them into json
    stations = session.query(Measurement.station).group_by(Measurement.station).all()
    list_of_stations = [i[0] for i in stations]
    return jsonify(list_of_stations)

# Returns temperature observed in json format
@app.route("/api/v1.0/tobs")
def tobs():
    #Get temerature observed data points convert them into json
    date_value = compute_latest_date()
    tobs_result = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= date_value).all()
    tobs_list = dict(tobs_result)
    return jsonify(tobs_list)

#Create an end-point to accept the start date for the query
@app.route("/api/v1.0/<start>")
def temp(start=None):
    #use the input date to apply it to the query and get the measurements and convert them into json
    list_of_measurements = []
    records = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.date).all()
    for i in records:
        row = { "date": i[0], "tobs_min" : i[1], "tobs_avg": i[2], "tobs_max": i[3] }
        list_of_measurements.append(row)
    
    return jsonify(list_of_measurements)

#Create an end-point to accept the start date for the query
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start=None,end=None):
    #use the input date RANGE to apply it to the query and get the measurements and convert them into json    
    list_of_measurements_period = []
    records_period = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start,Measurement.date <= end).group_by(Measurement.date).all()
    for i in records_period:
        row = { "date": i[0], "tobs_min" : i[1], "tobs_avg": i[2], "tobs_max": i[3] }
        list_of_measurements_period.append(row)
    #measurements=json.dumps(records)
    return jsonify(list_of_measurements_period)

#If user enters an end-point and there is no handler, then provide an appropriate response 
@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({'ERROR': 'Invalid end-point, please provide a valid URL'}), 404)

#Default load page
@app.route("/")
def welcome():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5009)