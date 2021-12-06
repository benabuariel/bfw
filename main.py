from flask import Flask, render_template, request, redirect, url_for
from api import API
from utilities import loc_list_to_human, sql_to_humans, is_valid_date
import database as db
from CONF import DB_FILE


app = Flask(__name__)
api = API()
db.init_db(DB_FILE)


@app.route('/')
def index():
        return render_template("home_page.html")


@app.route('/<location>/<day>/<month>/<year>')
def search_db(location, day, month, year):
    sql_query = db.get_weather_from(DB_FILE, location, int(year), int(month), int(day))
    if len(sql_query) == 0:
        return redirect(url_for('index', msg=f"{location} Not Found!"))
    else:
        sql_query = sql_query[-1]
    humidity, max_temp, min_temp = sql_to_humans(sql_query)
    zipped = zip(max_temp.items(), min_temp.items(), humidity.items())

    return render_template("playground.html",
                           Max_Temp=max_temp, Min_Temp=min_temp, Humidity=humidity,
                           ZippedItems=zipped)


@app.route('/', methods=['POST', 'GET'])
def user_input():
    text = request.form['text']
    if len(text) == 0:
        return render_template("home_page.html", msg=f"{text} Not Found!")
    date_ = request.form['date']
    api.__init__()
    if not (api.get_loc(text) or is_valid_date(date_)):
        return render_template("home_page.html", msg=f"{text} Not Found!")
    if len(date_) > 0:
        day, month, year = is_valid_date(date_)
        return redirect(url_for('search_db', location=text, day=day, month=month, year=year))
    return redirect(url_for('search_loc', location=text))


@app.route('/loc/<location>')
def search_loc(location):
    location_list = api.loc_list
    location_list = enumerate(loc_list_to_human(location_list))
    return render_template("choose_location.html", loc_list=location_list)


@app.route('/loc/<location>', methods=['POST'])
def choose_loc(location):
    op = request.form['options']
    return redirect(url_for('weather_present', location=location, option=op))


@app.route('/weather/<location>/<option>')
def weather_present(location, option):
    option = int(option)
    if not api.choose_city(option):  # need to check the return status code
        return redirect(url_for('/'))
    country = api.loc_list[option][1]
    dist = api.loc_list[option][3]
    city = api.loc_list[option][0]
    state = api.loc_list[option][2]
    max_temp = api.max_temp
    min_temp = api.min_temp
    humidity = api.humidity
    status = api.status
    zipped = zip(max_temp.items(), min_temp.items(), humidity.items())

    db.insert_db(DB_FILE, api)

    return render_template("playground.html",
                           Country=country, State=state, District=dist, City=city,
                           Max_Temp=max_temp, Min_Temp=min_temp, Humidity=humidity,
                           Status=status, ZippedItems=zipped)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
