# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
  
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Define a route to list all available routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

# Define route to convert precipitation data to JSON
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Most recent date in the dataset
    most_recent_date = dt.date(2017, 8, 23)

    # Calculate the date one year from the last date in data set
    year_ago = most_recent_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
                            filter(Measurement.date >= year_ago).all()

    # Convert the query results to a dictionary with date as key and prcp as value
    precipitation_dict = {}
    for date, prcp in precipitation_data:
        precipitation_dict[date] = prcp

    # Return JSON representation of the dictionary
    return jsonify(precipitation_dict)



# Define route to return JSON list of stations
@app.route("/api/v1.0/stations")
def stations():
    # Query total number of stations in the dataset
    total_stations = session.query(Station.station).all()

    # Extract the total number of stations from the query result
    all_names = list(np.ravel(total_stations))

    # Return JSON response with the total number of stations
   

    return jsonify(all_names)



# Define route to query and return JSON list of temperature observations
@app.route("/api/v1.0/tobs")
def tobs():
    # Query last 12 months of temperature observation data for the most active station
    most_recent_date = dt.date(2017, 8, 23)
    year_ago = most_recent_date - dt.timedelta(days=365)
    most_active_stations = session.query(Station.station, func.count(Station.station)).\
                        filter(Measurement.station==Station.station).\
                        group_by(Station.station).\
                        order_by(func.count(Station.station).desc()).all()
    
    most_active_station_id = most_active_stations[0][0]
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station==Station.station).\
                    filter(Station.station == most_active_station_id).\
                    filter(Measurement.date >= year_ago).all()


    # Create a list of dictionaries with date and temperature observation
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]

    # Return JSON list of temperature observations
    return jsonify(tobs_list)


# Define route to calculate temperature for a specified start date
@app.route("/api/v1.0/<start>")
def temp_start(start):
    # Query to calculate lowest, highest, and average temperature for all dates greater than or equal to the start date
    temperature_start = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                         filter(Measurement.date >= start).all()

    # Extract temperature from the query result
    tmin, tmax, tavg = temperature_start[0]

    # Return JSON response with temperature 
    return jsonify({"TMIN": tmin, "TAVG": tavg, "TMAX": tmax})

# Define route to calculate temperature for a specified start and end date
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    # Query to calculate lowest, highest, and average temperature for dates between the start and end dates, inclusive
    temperature_end = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                         filter(Measurement.date >= start).\
                         filter(Measurement.date <= end).all()

    # Extract temperature  from the query result
    tmin, tmax, tavg = temperature_end[0]

    # Return JSON response with temperature 
    return jsonify({"TMIN": tmin, "TAVG": tavg, "TMAX": tmax})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)














