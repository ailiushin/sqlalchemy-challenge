import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflecting existing database and tables into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

#saving references to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of active stations: /api/v1.0/stations<br/>"
        f"Temperature for one year for station USC00519281 : /api/v1.0/tobs<br/>"
        f"Min, Average & Max Temperatures for any given start date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Min, Average & Max Temperatures any given date range: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br>"
    )
#################################################
@app.route('/api/v1.0/precipitation')
def precipitation():
    #creating session link
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()

#creating a list and then populating it 
    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

#################################################

@app.route('/api/v1.0/stations')
def stations():
    #creating session link
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

#creatig a list then going through the query results and populating the variables
    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

#################################################

@app.route('/api/v1.0/tobs')
def tobs():
    #creating session link
    session = Session(engine)

    #calcuting the date, then quering for results for the last 12 months and then putting in into a list
    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(latest, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*sel).filter(Measurement.date >= querydate).all()
    session.close()

    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

#################################################

@app.route('/api/v1.0/<start>')
def start(start):
    #creating session link
    session = Session(engine)

    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

#creatig a list then going through the query results and calcuating min, max and average for selected date
    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

#################################################

@app.route('/api/v1.0/<start>/<stop>')
def start_stop(start,stop):
    #creating session link
    session = Session(engine)
    queryresult =  session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

#creatig a list then going through the query results and calcuating min, max and average for selected dates
    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

if __name__ == '__main__':
    app.run(debug=True)