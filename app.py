from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import numpy as np

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

def calc_temps(start_date, end_date):
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# Flask
app = Flask(__name__)

# Create routes
@app.route("/")
def welcome():
    return """
    Welcome to the Hawaii Climate API!
    Available endpoints: <br>
    /api/v1.0/precipitation <br>
    /api/v1.0/stations <br>
    /api/v1.0/tobs <br>
    /api/v1.0/&lt;start&gt; where start is a date in YYYY-MM-DD format <br> 
    /api/v1.0/&lt;start&gt;/&lt;end&gt; where start and end are dates in YYYY-MM-DD format
    """

@app.route("/api/v1.0/precipitation")
def precip():
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= "2012-02-28").\
    filter(Measurement.date <= "2012-03-05").all()

    results_dict = []
    for row in results:
        date_dict = {}
        date_dict[row.date] = row.prcp
        results_dict.append(date_dict)

    return jsonify(results_dict)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    results_list = list(np.ravel(results))

    return jsonify(results_list)

@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(Measurement.tobs).\
        filter(Measurement.date >= "2012-02-28").\
        filter(Measurement.date <= "2012-03-05").all()

    results_list = list(np.ravel(results))

    return jsonify(results_list)



@app.route("/api/v1.0/<start>")
def start_date(start):
    end_date = session.query(func.max(Measurement.date)).all()[0][0]
    temps = calc_temps(start, end_date)
    temps_list = list(np.ravel(temps))
    return jsonify(temps_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    temps = calc_temps(start, end)
    temps_list = list(np.ravel(temps))
    return jsonify(temps_list)

if __name__ == '__main__':
    app.run(debug=True)