import csv
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

restaurants = []

def hours_to_datetime(time):
    """Function converting hours (10PM/ 10:00PM) to datetime."""
    
    if ":" not in time:
        return datetime.strptime(time, "%I %p").time()
    return datetime.strptime(time, "%I:%M %p").time()



def parse_hours(hours):
    """Function parsing csv file into {name:, {Mon:{'open':, 'close':}, Tue:{'open':, 'close':}, ...}}"""

    days_of_week = ['Mon', 'Tues', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    hours_schedule = {}

    unique_sched = hours.split(" / ")
    for sched in unique_sched:

        days_output = []

        days = []
        hours = ""

        for i, char in enumerate(sched):
            if char.isdigit():
                hours = sched[i:]
                days = sched[:i-1]
                break

        if "," in days:
            multiple_days = days.split(", ")
            for day in multiple_days:
                if "-" in day:
                    days = day.split("-")
                    start = days_of_week.index(days[0])
                    end = days_of_week.index(days[1])
                    days_output = days_of_week[start:end + 1]
                else :
                    days_output.append(day)
        else :
            if "-" in days:
                days = days.split("-")
                start = days_of_week.index(days[0])
                end = days_of_week.index(days[1])
                days_output = days_of_week[start:end + 1]
            else :
                days_output.append(days)


        for day in days_output:
            hours_schedule[day] = {
                "open": hours.split("-")[0].strip(),
                "close": hours.split("-")[1].strip(),
            }
    return hours_schedule

def open_restaurants(day, time):
    """Function returning open restaurants (day: Mon/Tues/Wed/... ,time: 12PM OR 12:00PM)."""

    open_restaurants_list = []

    time_to_check = hours_to_datetime(time)

    for restaurant in restaurants:
        hours = restaurant["hours"]

        if day in hours:
            restaurant_open = hours_to_datetime(hours[day]['open'])
            restaurant_close = hours_to_datetime(hours[day]['close'])

            if restaurant_open <= time_to_check <= restaurant_close:
                open_restaurants_list.append(restaurant["name"])

    return open_restaurants_list

def csv_to_restaurant():
    """Function reading csv file and storing data in restaurants list."""
    with open('restaurants.csv', 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        header = next(reader)

        for items in reader:
            restaurant_name = items[0]
            restaurant_hours = parse_hours(items[1])

            restaurants.append({
                "name": restaurant_name,
                "hours": restaurant_hours
            })

def run_web_server():
    """DateTime example - 2024-12-13 11:37:33.114709"""
    @app.route('/', methods=['GET'])
    def get_open_restaurants():
        datetime_var = request.args.get('datetime')

        day_of_week = datetime.strptime(datetime_var, "%Y-%m-%d %H:%M:%S.%f").strftime("%a")
        time = datetime.strptime(datetime_var.split(" ",1)[1].strip(), "%H:%M:%S.%f").strftime("%I:%M %p")

        return jsonify(open_restaurants(day_of_week, time))

    if __name__ == '__main__':
        app.run(debug=True, port=8080)

csv_to_restaurant()
run_web_server()
