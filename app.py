#depedencies
from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct, desc

#create directory to sqlite file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#define flask
app = Flask(__name__)

@app.route("/")
#create starting point for API, privde information
def welcome():
    return(
        f"welcome to the Hawaii weather API!<br>"
        f"available routes:<br>"
        f"/api/v1.0/precipation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start_date<br>"
        f"/api/v1.0/start_date/end_date<br>"
        f"NOTE: dates must be in YYYY-MM-DD format!"
)
@app.route("/api/v1.0/precipation")
def prcp():
        # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query data needed
    results = session.query(Measurement.date, Measurement.prcp).all()
#close the session
    session.close()
    #set up dictionary to jsonify
    prcp_dct = {}
    #set date as key, precipitation as values
    for date, prcp in results:
            prcp_dct[date] = prcp


#jsonify it to return with API data
    return jsonify(prcp_dct)



@app.route("/api/v1.0/stations")
def station():
        #set up session
    session = Session(engine)

    # Query data needed
    results = session.query(Station.station).all()

    #close the session
    session.close()
    #move data to a list that can be jsonified
    stations = list(np.ravel(results))
    return jsonify(stations)

   
@app.route("/api/v1.0/tobs")
def tobs():
        session = Session(engine)
        # Design a query to retrieve the last 12 months of precipitation data and plot the results

# Calculate the date 1 year ago from the last data point in the database
        max_date=max(session.query(func.date(Measurement.date)))
        #making the data dynamic
        separate = max_date[0].split('-')
        #getting the date that is 365 before the most recent date
        oldest_date = dt.date(int(separate[0]),int(separate[1]),int(separate[2])) - dt.timedelta(days=365) 
# Perform a query to retrieve the data and precipitation scores
        year_tobs = session.query(Measurement.tobs).filter(Measurement.date >= oldest_date).all()
        session.close()
        #move data to a list that can be jsonified
        tobs = list(np.ravel(year_tobs))
        return jsonify(tobs)
@app.route("/api/v1.0/<date>")
def start(date):
        #start session
        session = Session(engine)
        #filter by the date provided
        tobs_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= date).all()
        #move to list
        tobs_stats_list = list(np.ravel(tobs_stats))
        session.close()
        return(jsonify(tobs_stats_list))
@app.route("/api/v1.0/<start>/<end>")
def end(start, end):          
        session = Session(engine)
        #filter by the provided dates
        tobs_stats = session.query(Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
        #create dictionary for the data
        dict_stats = {}
        #set date to key, and put min, avg, max as callable list
        for date, min, avg, max in tobs_stats:
                dict_stats[date] = [min,avg,max]
        return(jsonify(dict_stats))
if (__name__ == "__main__"):
   app.run(debug=True)


