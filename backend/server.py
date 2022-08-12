import json
import sqlite3
from datetime import date
import traceback
from flask import Flask, request, send_from_directory

# Project imports
from config import Config


# Globals
config = None


# Main Flask web server application
app = Flask(__name__)


@app.route('/')
# Serves the index.html
def get_index():
    '''Serves the index.html.'''
    return send_from_directory("../site", "index.html")


@app.route('/<path:path>')
# Serves all other static files
def get_file(path):
    '''Serves all other static files.'''
    return send_from_directory("../site", path)


# Returns JSON response containing current data
def get_json_data_current():
    '''Returns JSON response containing current data'''
    con = sqlite3.connect("../data/db.sqlite")
    cur = con.cursor()
    # Current
    cur.execute("SELECT * FROM current")
    rows_cur = cur.fetchall()
    # All time
    cur.execute("SELECT * FROM all_time")
    rows_all = cur.fetchall()
    # Today
    day_string = str(date.today())
    cur.execute(f"SELECT * FROM days WHERE date='{day_string}'")
    rows_today = cur.fetchall()
    # Done
    con.commit()
    con.close()
    # Compute earnings
    price = float(config.config_data['prices']['price_per_grid_kwh'])
    revenue = float(config.config_data['prices']['revenue_per_fed_in_kwh'])
    earned_total = rows_all[0][6] * revenue
    saved_total = (rows_all[0][2] - rows_all[0][6]) * (price - revenue)
    earned_today = rows_today[0][6] * revenue
    saved_today = (rows_today[0][2] - rows_today[0][6]) * (price - revenue)
    # Build response data
    data = {
        "state": "ok",
        "currently_produced_kw": rows_cur[0][1],
        "currently_consumed_kw": rows_cur[0][2],
        "currently_fed_in_kw": rows_cur[0][3],
        "all_time_produced_kwh": rows_all[0][2],
        "all_time_consumed_kwh": rows_all[0][4],
        "all_time_fed_in_kwh": rows_all[0][6],
        "all_time_earned": (earned_total + saved_total),
        "today_produced_kwh": rows_today[0][2],
        "today_consumed_kwh": rows_today[0][4],
        "today_fed_in_kwh": rows_today[0][6],
        "today_earned": (earned_today + saved_today)
    }
    return json.dumps(data)


# Returns JSON response containing available years
def get_json_data_dates():
    '''Returns JSON response containing available years.'''
    con = sqlite3.connect("../data/db.sqlite")
    cur = con.cursor()
    cur.execute("SELECT min(date) FROM years")
    rows = cur.fetchall()
    con.commit()
    con.close()
    data = {
        "state": "ok",
        "year_min": rows[0][0],
        "year_max": int(date.today().strftime("%Y")),
    }
    return json.dumps(data)


# Returns JSON response containing daily data for a month
def get_json_data_days_in_month(year_and_month):
    '''Returns JSON response containing daily data for a month.'''
    con = sqlite3.connect("../data/db.sqlite")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM days WHERE date LIKE '{year_and_month}%'")
    rows = cur.fetchall()
    con.commit()
    con.close()
    # Build results
    data = []
    for row in rows:
        data.append({
            "date": row[0],
            "produced": row[2] - row[1],
            "consumed": row[4] - row[3],
            "fed_in": row[6] - row[5]
        })
    return json.dumps(data)


# Returns JSON response containing monthly data for a year
def get_json_data_months_in_year(year):
    '''Returns JSON response containing monthly data for a year.'''
    con = sqlite3.connect("../data/db.sqlite")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM months WHERE date LIKE '{year}%'")
    rows = cur.fetchall()
    con.commit()
    con.close()
    # Build results
    data = []
    for row in rows:
        data.append({
            "date": row[0],
            "produced": row[2] - row[1],
            "consumed": row[4] - row[3],
            "fed_in": row[6] - row[5]
        })
    return json.dumps(data)


# Returns JSON response containing monthly data for a year
def get_json_data_real_time():
    '''Returns JSON response containing monthly data for a year.'''
    con = sqlite3.connect("../data/db.sqlite")
    cur = con.cursor()
    cur.execute("SELECT * FROM real_time")
    rows = cur.fetchall()
    con.commit()
    con.close()
    return json.dumps(rows)


# Returns JSON response containing historical data
def get_json_data_history(table, search_date):
    '''Returns JSON response containing historical data.'''
    con = sqlite3.connect("../data/db.sqlite")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE date='{search_date}'")
    rows = cur.fetchall()
    con.commit()
    con.close()
    # Compute feed in
    consumed_self = rows[0][2] - rows[0][6]
    consumed_grid = rows[0][4] - consumed_self
    consumed_total = consumed_self + consumed_grid
    consumed_self_rel = (consumed_self / consumed_total) * 100.0
    consumed_grid_rel = (consumed_grid / consumed_total) * 100.0
    # Compute usage
    usage_fed_in_rel = rows[0][6] / rows[0][2] * 100.0
    usage_self_consumed_rel = consumed_self / rows[0][2] * 100.0
    # Compute earnings
    price = float(config.config_data['prices']['price_per_grid_kwh'])
    revenue = float(config.config_data['prices']['revenue_per_fed_in_kwh'])
    earned = rows[0][6] * revenue
    saved = (rows[0][2] - rows[0][6]) * (price - revenue)
    # Build response data
    data = {
        "state": "ok",
        "produced_kwh": rows[0][2],
        "consumed_total_kwh": rows[0][4],
        "consumed_from_pv_kwh": consumed_self,
        "consumed_from_grid_kwh": consumed_grid,
        "consumed_from_pv_percent": consumed_self_rel,
        "consumed_from_grid_percent": consumed_grid_rel,
        "usage_fed_in_kwh": rows[0][6],
        "usage_self_consumed_kwh": consumed_self,
        "usage_fed_in_percent": usage_fed_in_rel,
        "usage_self_consumed_percent": usage_self_consumed_rel,
        "earned_feedin": earned,
        "earned_savings": saved,
        "earned_total": (earned+saved),
    }
    return json.dumps(data)


# .../query?type=current
# .../query?type=dates
# .../query?type=historical&table=days&date=2022-08-03
# etc.
@app.route("/query", methods=['GET'])
def handle_request():
    '''Answers all query requests.'''
    try:
        _type = request.args['type']
        if config.verbose_logging:
            print(f"Server: REST request of type '{_type}' received")

        if _type == "current":
            data = get_json_data_current()
            return data
        elif _type == "dates":
            data = get_json_data_dates()
            return data
        elif _type == "historical":
            table = request.args['table']
            _date = request.args['date']
            if config.verbose_logging:
                print(f"  Request details: table: '{table}', date: {_date}")
            data = get_json_data_history(table, _date)
            return data
        elif _type == "real_time":
            data = get_json_data_real_time()
            return data
        elif _type == "days_in_month":
            _month = request.args['date']
            data = get_json_data_days_in_month(_month)
            return data
        elif _type == "months_in_year":
            _year = request.args['date']
            data = get_json_data_months_in_year(_year)
            return data
    except Exception:
        print("Server: Error:")
        print(traceback.print_exc())
        data = {"state": "error"}
        return json.dumps(data)


# Main loop
def main():
    '''Main loop.'''

    global config

    # Read the configuration from disk
    try:
        print("Grabber: Reading backend configuration from config.yml")
        config = Config("data/config.yml")
    except Exception:
        exit()

    # Start the web server
    if __name__ == '__main__':
        app.run(
            host=config.config_data['server']['ip'],
            port=config.config_data['server']['port'])


# Main entry point of the application
if __name__ == "__main__":
    main()