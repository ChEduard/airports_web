# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 12:33:45 2023

@author: ED
"""

import mysql.connector
import flask
import config

app = flask.Flask(__name__)
template = 'index.html'

@app.route('/')
def index():
    return flask.render_template(template)

@app.route('/top.html')
def top():
    global departure
    departure = (flask.request.args.get('departure'))
    global arrival
    arrival = (flask.request.args.get('arrival'))
    return flask.render_template('top.html')

@app.route('/bottom.html')
def airports():
    cnx = mysql.connector.connect(user=config.user,
                                  password=config.password,
                                  host=config.host,
                                  database=config.database)
    cursor = cnx.cursor()

    global departure
    departure = (flask.request.args.get('departure'))
    global arrival
    arrival = (flask.request.args.get('arrival'))

    query = find_route_query(departure, arrival)
    cursor.execute(query)

    cont = '<table border="2" align="center" rules="all" width="1000" height="20">\
    <tr><th colspan=4>Departure</th><th colspan=4>Arrival</th></tr>\
    <tr><th>Country</th><th>City</th><th>Airport</th><th>IATA</th><th>Country</th><th>City</th><th>Airport</th><th>IATA</th></tr>'
    for (country1, city1, airport1,  airno1, airno2, airport2, city2, country2) in cursor:
      link = 'a'
      cont += f'<tr><td>{country1}</td><td>{city1}</td><td>{airport1}</td><td>{airno1}</td><td>{country2}</td><td>{city2}</td><td>{airport2}</td><td>{airno2}</td></tr>'
    cursor.close()
    cont += '</table>'
    cnx.close()
    return cont



def find_route_query(depart, arrive):
    """
    Forming request string to MySQL by departure/arrival IATA/airport/city/country
    :param depart: str
    :param arrive:  str
    :return: str
    """
    if depart != None and arrive != None:
        if len(depart) == 3:
            depart_query = f'r.src_airport="{depart}"'
        else:
            depart_query = f'ap.airport LIKE "%{depart}%" OR ap.city LIKE "%{depart}%" OR ap.country LIKE "%{depart}%"'

        if len(arrive) == 3:
            arrive_query = f'r.dst_airport="{arrive}"'
        else:
            arrive_query = f'ap2.airport LIKE "%{arrive}%" OR ap2.city LIKE "%{arrive}%" OR ap2.country LIKE "%{arrive}%"'

        main_query = 'SELECT ap.country, ap.city, ap.airport, r.src_airport, r.dst_airport, ap2.airport, ap2.city, ap2.country \
                        FROM airports AS ap INNER JOIN routes AS r ON ap.iata = r.src_airport INNER JOIN airports AS ap2 ON ap2.iata = r.dst_airport \
                        WHERE ('

        if len(depart_query) > 0:
            if len(arrive_query) > 0:
                query = (main_query + depart_query + ') AND (' + arrive_query + ')')
            else:
                query = (main_query + depart_query + ')')
        else:
            if len(arrive_query) > 0:
                query = (main_query + arrive_query + ')')
        return query
    else:
        query = (f'''SELECT ap.country, ap.city, ap.airport, r.src_airport, r.dst_airport, ap2.airport, ap2.city, ap2.country 
            FROM airports AS ap INNER JOIN routes AS r ON ap.iata = r.src_airport INNER JOIN airports AS ap2 ON ap2.iata = r.dst_airport 
            WHERE ap.city LIKE "%Petersburg%"''')
        return query


if __name__ == '__main__':
    app.run()