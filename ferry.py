from threading import Thread
from datetime import datetime
from pytz import timezone
from flask import render_template
import math
import requests
import json
import os
import time
import smtplib


# Copyright 2021 Johnathan Pennington | All rights reserved.


ROUTES_API_KEY = os.getenv("ROUTES_API_KEY")
WSDOT_API_KEY = os.getenv("WSDOT_API_KEY")
SENDER = os.getenv("SENDER")
SENDER_PASS = os.getenv("SENDER_PASS")
RECIPIENT = os.getenv("RECIPIENT")

ferry_data_thread = None

# # SAMPLE DATA
# location_info = {'status': 'ok', 'origin coords': '47.76011099999999,-122.2054452', 'destination coords': '47.7987072,-122.4981921', 'depart terminal': 0}
# ferry_data = {'cache timestamp': 1639170125, 'alerts': [{'RouteAlertText': 'Reminder: Temporary Schedule Changes Continue for Several Routes on Friday, December 9. See Bulletin for details.', 'BulletinText': '<p><span style="font-family: lato; font-size: 14px;">Washington State Ferries is operating on alternate schedules on most routes until further notice. These changes will help offer more predictable and reliable service systemwide in the face of crewing shortages due to a global of shortage mariners that has been worsened by the pandemic. WSF will attempt to add service when possible, and will provide notifications when full service can temporarily be restored to a route.</span></p>\r\n<p><span style="font-family: lato; font-size: 14px;">For Friday December 10, the following routes are operating on alternate schedules:</span><o:p></o:p></p>\r\n<ul>\r\n<li><span style="font-family: lato; font-size: 14px;">The Seattle/Bremerton route remains on one-boat service until further notice. The Chimacum is currently operating <a href="https://www.wsdot.com/ferries/schedule/scheduledetailbyroute.aspx?route=sea-br">only the #2 sailings on the route’s schedule</a> .\xa0</span></li>\r\n<li><span style="font-family: lato; font-size: 14px;"><a href="https://www.wsdot.com/Ferries/Schedule/scheduledetailbyroute.aspx?schedrouteid=2081&amp;route=f-v-s">Fauntleroy/Vashon/Southworth</a>: Daily two-boat schedule instead of three</span></li>\r\n</ul>\r\n<p>For Friday, Dec. 10, the following routes are operating on their fall schedules:</p>\r\n<ul>\r\n<li><a href="https://wsdot.com/Ferries/Schedule/scheduledetailbyroute.aspx?schedrouteid=2070&amp;route=ana-sj-sid">Anacortes/San Juan Islands</a><span>: Reservations remain suspended until further notice</span></li>\r\n<li><a href="https://www.wsdot.com/ferries/schedule/scheduledetailbyroute.aspx?route=sea-bi" class="content_text">Seattle / Bainbridge Island Schedule</a>\xa0</li>\r\n<li><a href="https://www.wsdot.com/ferries/schedule/scheduledetailbyroute.aspx?route=muk-cl">Mukilteo / Clinton Schedule</a>\xa0</li>\r\n<li><a id="cphPageTemplate_rprSchedRoutesInActive_hylScheduledRoute_1" href="https://wsdot.com/ferries/schedule/scheduledetailbyroute.aspx?schedrouteid=2076&amp;route=ed-king">Edmonds/Kingston</a></li>\r\n</ul>\r\n<p>Reservations for San Juan Islands Route:</p>\r\n<p>New reservations for travel in the San Juan Islands are unavailable until further notice.\xa0 Existing reservation holders will be loaded on a first-come, first served basis but will be prioritized over vehicles without an existing reservation.\xa0 Those passengers who need to travel standby without a reservation may encounter delays and should get to the terminal early.</p>\r\n<p>Customers who choose not to travel during this time will not incur a no-show fee.\xa0</p>\r\n<p>We will continue to provide updates as they become available. Thank you for your patience and understanding while we work to provide reliable service during this challenging time.</p>\r\n<p><span style="font-family: lato; font-size: 14px;"></span></p>\r\n<p><span style="font-family: lato; font-size: 14px;">The <a href="https://www.wsdot.com/ferries/schedule/default.aspx">schedule page online</a> shows the currently active schedules in the top section, and the inactive schedules are below.\xa0 Please note that the active schedules may change daily depending on crew availability, so please be sure to monitor email alerts and check the <a href="https:/www.wsdot.wa.gov/ferries/schedule/bulletin.aspx">Travel Alert Bulletins</a> page for updates.\xa0</span></p>'}, {'RouteAlertText': 'Edm/King -Edmonds/Kingston to Remain on One-Boat Service Dec. 15 & 16', 'BulletinText': '<p>One-boat service will be maintained on the Edmonds/Kingston for a couple days later this month regardless of crew availability. The Spokane will be the only boat operating on the route starting Wednesday, Dec. 15 through at least Thursday, Dec. 16. Due to unplanned maintenance to other boats in the fleet, WSF must shift vessels to best meet traffic demands systemwide.</p>\r\n<p>Thank you for your patience while we work to maintain our fleet.</p>'}, {'RouteAlertText': 'Masks Required Only in Indoor Areas of Terminals and Vessels', 'BulletinText': '<p>Face masks are now required only in indoor areas of our terminals and vessels for all riders and employees in <a href="https://www.cdc.gov/coronavirus/2019-ncov/travelers/face-masks-public-transportation.html">compliance with the latest CDC guidelines</a>. All customers inside terminals or vessels should continue to wear face coverings. However, passengers can remove their masks while outdoors on the sun deck, car deck areas of the vessel, outside waiting areas at terminals and other outdoor locations. Please remember to mask up upon reentering interior areas of boats and terminals.</p>'}, {'RouteAlertText': 'Edm/King - Edmonds Terminal Holding Lane Partial Closures Began October 11', 'BulletinText': '<p>Beginning on Monday, Oct. 11, a contractor for the City of Edmonds has been using one of the terminal holding lanes on State Route 104/Edmonds Way from <strong>6 a.m. Mondays through 4:30 p.m. Thursdays</strong> for several months. <strong>Both approach lanes will be open for ferry travelers Thursday evenings through Sunday and holidays.</strong> We appreciate your support while the City of Edmonds conducts important sewer work. We will keep you informed as this continues.</p>'}], 'schedules': {'terminal 0': {'route 0': [1639143000, 1639145400, 1639148700, 1639151700, 1639154700, 1639157700, 1639161600, 1639164300, 1639167900, 1639170600, 1639173900, 1639177200, 1639180200, 1639183500, 1639187100, 1639189800, 1639193400, 1639196100, 1639200000, 1639202700, 1639205400, 1639210500], 'route 1': [1639143300, 1639145400, 1639149000, 1639151700, 1639155000, 1639157700, 1639160400, 1639163100, 1639166100, 1639168800, 1639172100, 1639175100, 1639178100, 1639180500, 1639183500, 1639185900, 1639188900, 1639191600, 1639194000, 1639197000, 1639199100, 1639201800, 1639203900, 1639206600, 1639208700]}, 'terminal 1': {'route 0': [1639140300, 1639142400, 1639146000, 1639148700, 1639151700, 1639154700, 1639158000, 1639160700, 1639164600, 1639167600, 1639170900, 1639173900, 1639176900, 1639180200, 1639183500, 1639186500, 1639190400, 1639192800, 1639196400, 1639198800, 1639202400, 1639207800], 'route 1': [1639140300, 1639143000, 1639146300, 1639148400, 1639151700, 1639154400, 1639157700, 1639160400, 1639163100, 1639166100, 1639169100, 1639171800, 1639175400, 1639177800, 1639180800, 1639183200, 1639186200, 1639188600, 1639191600, 1639194300, 1639196400, 1639199400, 1639201200, 1639204200, 1639206600]}}}
# routes_info = ['\n<h3>VIA THE SEATTLE FERRY TERMINAL:</h3>\n<table>\n    <tr>\n        <td class="table-col-left">DEPART ORIGIN:</td>\n        <td class="table-col-right">08:20 AM <span>(in 6 minutes)</span></td>\n    </tr>\n    <tr>\n        <td class="table-col-left">DRIVE TO FERRY:</td>\n        <td class="table-col-right">35 minutes</td>\n    </tr>\n    <tr>\n        <td class="table-col-left">FERRY DEPARTURE:</td>\n        <td class="table-col-right">08:55 AM</td>\n    </tr>\n    <tr>\n        <td class="table-col-left">FERRY CROSSING TIME:</td>\n        <td class="table-col-right">35 minutes</td>\n    </tr>\n    <tr>\n        <td class="table-col-left">DRIVE FROM FERRY:</td>\n        <td class="table-col-right">3 minutes</td>\n    </tr>\n    <tr>\n        <td class="table-col-left"><strong>TOTAL TRAVEL TIME:</strong></td>\n        <td class="table-col-right"><strong>73 minutes</strong></td>\n    </tr>\n    <tr>\n        <td class="table-col-left white"><strong>FINAL DESTINATION:</strong></td>\n        <td class="table-col-right white"><strong>09:33 AM</strong></td>\n    </tr>\n</table>', '\n<h3>VIA THE EDMONDS FERRY TERMINAL:</h3>\n<table>\n    <tr>\n        <td class="table-col-left">DEPART ORIGIN:</td>\n        <td class="table-col-right">08:21 AM <span>(in 7 minutes)</span></td>\n    </tr>\n    <tr>\n        <td class="table-col-left">DRIVE TO FERRY:</td>\n        <td class="table-col-right">29 minutes</td>\n    </tr>\n    <tr>\n        <td class="table-col-left">FERRY DEPARTURE:</td>\n        <td class="table-col-right">08:50 AM</td>\n    </tr>\n    <tr>\n        <td class="table-col-left">FERRY CROSSING TIME:</td>\n        <td class="table-col-right">30 minutes</td>\n    </tr>\n    <tr>\n        <td class="table-col-left">DRIVE FROM FERRY:</td>\n        <td class="table-col-right">27 minutes</td>\n    </tr>\n    <tr>\n        <td class="table-col-left"><strong>TOTAL TRAVEL TIME:</strong></td>\n        <td class="table-col-right"><strong>86 minutes</strong></td>\n    </tr>\n    <tr>\n        <td class="table-col-left white"><strong>FINAL DESTINATION:</strong></td>\n        <td class="table-col-right white"><strong>09:47 AM</strong></td>\n    </tr>\n</table>', '\n<h3>VIA THE TACOMA NARROWS BRIDGE:<br><span>(no ferry)</span></h3>\n<table>\n    <tr>\n        <td class="table-col-left">DEPART ORIGIN:</td>\n        <td class="table-col-right">Now</td>\n    </tr>\n    <tr>\n        <td class="table-col-left"><strong>TOTAL TRAVEL TIME:</strong></td>\n        <td class="table-col-right"><strong>114 minutes</strong></td>\n    </tr>\n    <tr>\n        <td class="table-col-left white"><strong>FINAL DESTINATION:</strong></td>\n        <td class="table-col-right white"><strong>10:08 AM</strong></td>\n    </tr>\n</table>']

# ROUTE 0
#     TERMINAL 0 = Seattle
#     TERMINAL 1 = Bainbridge
# ROUTE 1
#     TERMINAL 0 = Edmonds
#     TERMINAL 1 = Kingston
FERRY_ROUTES = [
    {
        "crossing minutes": 35,
        "terminals": [
            {
                "name": "Seattle",
                "terminal id": 7,
                "address": "801 Alaskan Way, Seattle, WA 98104",
            },
            {
                "name": "Bainbridge",
                "terminal id": 3,
                "address": "Ferry Dock, Bainbridge Island, WA 98110",
            },
        ]
    },
    {
        "crossing minutes": 30,
        "terminals": [
            {
                "name": "Edmonds",
                "terminal id": 8,
                "address": "Edmonds Way, Edmonds, WA 98020"
            },
            {
                "name": "Kingston",
                "terminal id": 12,
                "address": "Kingston, WA 98346"
            },
        ]
    },
]


def render_home_template():
    start_new_ferry_data_thread()
    return render_template('ferryhome.html')


def render_results_template(origin, destination):

    global ferry_data_thread

    # If not updated 3 minutes prior or less and cache is outdated, attempt to get updated ferry data.
    # Runs on separate thread while simultaneously running check_route_coords below on main thread.
    start_new_ferry_data_thread()

    if origin == '':
        return render_template(
            'ferryhome.html', error='Please enter an origin.', origin=origin, destination=destination)
    if destination == '':
        return render_template('ferryhome.html', error='Please enter a destination.',
                               origin=origin, destination=destination)

    location_info = check_route_coords(origin, destination)
    if location_info['status'] == 'error':
        admin_alert_thread(
            'Web App - ERROR',
            f'SoundX\nError at check_route_coords().\nORIGIN: {origin}\nDESTINATION: {destination}\n'
            f'MESSAGE: {location_info["message"]}'
        )
        return render_template('ferryhome.html', error=location_info['message'], origin=origin, destination=destination)

    if ferry_data_thread is not None:
        if ferry_data_thread.is_alive():
            ferry_data_thread.join(timeout=10.0)
    with open('ferrycache.json', 'r') as file:
        ferry_data = json.load(file)

    routes_info = get_info_all_routes(
        location_info['origin coords'], location_info['destination coords'],
        location_info['depart terminal'], ferry_data['schedules']
    )
    if routes_info == 'error':
        admin_alert_thread(
            'Web App - ERROR',
            f'SoundX\nError at get_info_all_routes().\nORIGIN: {origin}\nDESTINATION: {destination}'
        )
        return render_template(
            'ferryhome.html', error='Sorry, there was a problem retrieving route data. '
                                    'Please check your connection and try again.',
            origin=origin, destination=destination
        )

    admin_alert_thread('Web App - Log', f'SoundX\nRequest successful. Rendered ferryresults.html.\n'
                                        f'ORIGIN: {origin}\nDESTINATION: {destination}')
    return render_template(
        'ferryresults.html', data=routes_info, ferry_alerts=ferry_data['alerts'], origin=origin, destination=destination
    )


def start_new_ferry_data_thread():

    global ferry_data_thread

    if ferry_data_thread is not None:
        if ferry_data_thread.is_alive():
            return

    with open('ferrycache.json', 'r') as file:
        ferry_data = json.load(file)
    if time.time() - ferry_data['cache timestamp'] < 180:  # If cache was updated less than 3 minutes ago.
        return

    ferry_data_thread = Thread(target=get_ferry_data)
    ferry_data_thread.start()
    return


def admin_alert(subject, message):

    pacific_tz = timezone("US/Pacific")
    time_to_format = datetime.fromtimestamp(time.time(), tz=pacific_tz)
    second = round(float(time_to_format.strftime("%S.%f")), 2)
    formatted_datetime = time_to_format.strftime(f"%Y-%m-%d %H:%M:{second}")
    message = f'{formatted_datetime}\nPortfolio\n{message}\n{time.time()}'

    connection = smtplib.SMTP("smtp.mail.yahoo.com", port=587)  # or port=465
    connection.starttls()  # Make connection secure
    connection.login(user=SENDER, password=SENDER_PASS)
    connection.sendmail(
        from_addr=SENDER,
        to_addrs=RECIPIENT,
        msg=f"Subject: {subject}\n\n{message}"
    )
    connection.close()


def admin_alert_thread(subject, message):
    alert_args = [subject, message]
    alert_thread = Thread(target=admin_alert, args=alert_args)
    alert_thread.start()


def get_coords(address):
    """Returns dictionary. Keys: lat, long, county. Returns "error" if error."""

    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"  # plus params
    params = {
        "address": address,
        "key": ROUTES_API_KEY,
        "language": "en",
        "bounds": "48.4,-120.5|47.0,-123.4",
        # Area within which to bias search results. NE corner | SW corner.
        # Victoria BC: 48.4, -123.4  # Ellensburg WA: 47.0, -120.5
    }
    response = requests.get(endpoint, params=params)

    if response.json()["status"] != "OK":
        Exception("Could not get location data from Google API.")
        return "error"

    lat = response.json()["results"][0]["geometry"]["location"]["lat"]
    long = response.json()["results"][0]["geometry"]["location"]["lng"]
    address_components = response.json()["results"][0]["address_components"]

    county = None
    for component in address_components:
        for comp_type in component["types"]:
            if comp_type == "administrative_area_level_2":
                county = component["long_name"]
                break

    if county is None:
        Exception("Could not determine county from Google API.")
        return "error"

    return {"lat": lat, "long": long, "county": county, }


def get_drive_secs(depart_timestamp, origin, destination, traffic_model):
    """Rounds up number of seconds to equal an integer number of minutes. Returns "error" if error.
Traffic_model can be pessimistic, optimistic, or best_guess. \
Avoid can be none (default), tolls, highways, ferries, or indoor."""

    endpoint = "https://maps.googleapis.com/maps/api/distancematrix/json"  # plus params
    params = {
        "origins": origin,
        "destinations": destination,
        "key": ROUTES_API_KEY,
        "units": "imperial",
        "departure_time": int(depart_timestamp),
        "traffic_model": traffic_model,
        "avoid": "ferries",
    }
    response = requests.get(endpoint, params=params)

    if response.json()["status"] != "OK":
        Exception("Could not get route data from Google API.")
        return "error"

    drive_secs = response.json()["rows"][0]["elements"][0]["duration_in_traffic"]["value"]
    drive_mins_round_up = math.ceil(drive_secs / 60)
    return drive_mins_round_up * 60


def get_ferry_cache_flush_timestamp():
    endpoint_root = "https://www.wsdot.wa.gov/ferries/api/schedule/rest"
    endpoint = f"{endpoint_root}/cacheflushdate?apiaccesscode={WSDOT_API_KEY}"
    response = requests.get(endpoint)
    response.raise_for_status()
    timestamp = int(response.json()[6:-7]) / 1000
    return timestamp


def get_ferry_schedule(route, terminal):
    """Returns a list of departure timestamps."""

    departing_term_id = FERRY_ROUTES[route]["terminals"][terminal]["terminal id"]
    arriving_term_id = FERRY_ROUTES[route]["terminals"][terminal * -1 + 1]["terminal id"]
    endpoint_root = "https://www.wsdot.wa.gov/ferries/api/schedule/rest"
    only_remaining_times = "false"
    endpoint = f"{endpoint_root}/scheduletoday/{departing_term_id}/{arriving_term_id}/{only_remaining_times}" \
               f"?apiaccesscode={WSDOT_API_KEY}"

    response = requests.get(endpoint)
    # 1st depart_time_str = response["TerminalCombos"][0]["Times"][0]["DepartingTime"]
    # sample depart_time_str = "/Date(1621174200000-0700)/" = Sun May 16 2021 07:10:00 GMT-0700 (PDT)
    response.raise_for_status()

    departure_list = []
    for departure in response.json()["TerminalCombos"][0]["Times"]:
        depart_str = departure["DepartingTime"]
        depart_timestamp = int(int(depart_str[6:-7]) / 1000)
        departure_list.append(depart_timestamp)

    return departure_list


def get_ferry_alerts():
    endpoint_root = "https://www.wsdot.wa.gov/ferries/api/schedule/rest"
    endpoint = f"{endpoint_root}/alerts?apiaccesscode={WSDOT_API_KEY}"
    response = requests.get(url=endpoint)
    response.raise_for_status()
    json_data = response.json()

    route_ids = [5, 6]  # Route IDs: Edmonds/Kingston=6, Seattle/Bainbridge=5
    relevant_alerts = []
    for alert in json_data:
        relevant_alert = False
        for affected_route_id in alert["AffectedRouteIDs"]:
            if affected_route_id in route_ids:
                relevant_alert = True
                break
        if relevant_alert:
            trimmed_alert = {'RouteAlertText': alert['RouteAlertText'], 'BulletinText': alert['BulletinText']}
            relevant_alerts.append(trimmed_alert)

    return relevant_alerts


def validate_ferry_cache(ferry_cache):
    """Returns True if ferry cache is valid, and False if ferry cache is corrupt."""

    if 'cache timestamp' in ferry_cache:
        if not isinstance(ferry_cache['cache timestamp'], int):
            return False
    else:
        return False

    if 'alerts' in ferry_cache:
        for alert in ferry_cache['alerts']:
            if 'RouteAlertText' not in alert or 'BulletinText' not in alert:
                return False
    else:
        return False

    if 'schedules' in ferry_cache:
        for term in ['terminal 0', 'terminal 1']:
            if term in ferry_cache['schedules']:
                for rout in ['route 0', 'route 1']:
                    if rout in ferry_cache['schedules'][term]:
                        for timestamp in ferry_cache['schedules'][term][rout]:
                            if not isinstance(timestamp, int):
                                return False
                    else:
                        return False
            else:
                return False
    else:
        return False

    return True  # If not returned False in all tests above, returns True.


def try_ferry_alert_request(ferry_cache):
    """Returns dictionary with keys: source, data. Source value can be new, cache, or error."""
    try:
        alerts = {
            'source': 'new',
            'data': get_ferry_alerts(),
        }
    except:
        try:
            alerts = {
                'source': 'cache',
                'data': ferry_cache['alerts'],
            }
        except:
            alerts = {
                'source': 'error',
                'data': 'error',
            }
        # else: Error with getting updated ferry alerts from API. Using potentially outdated cache.

    return alerts


def try_ferry_sched_request(term, rout, ferry_cache):
    """Returns dictionary with keys: source, data. Source value can be new, cache, or error."""

    try:
        sched = {
            'source': 'new',
            'data': get_ferry_schedule(rout, term),
        }
    except:
        try:
            sched = {
                'source': 'cache',
                'data': ferry_cache['schedules'][f'terminal {term}'][f'route {rout}'],
            }
        except:
            sched = {
                'source': 'error',
                'data': 'error',
            }
            admin_alert_thread(
                'Web App - ERROR',
                f'SoundX\nError at try_ferry_sched_request().\nROUTE {rout} | TERMINAL {term}\n'
                f'MESSAGE: Error with getting updated ferry schedule from API. Also unable to use cache. Total fail.'
            )

        else:
            admin_alert_thread(
                'Web App - ERROR',
                f'SoundX\nError at try_ferry_sched_request().\nROUTE {rout} | TERMINAL {term}\n'
                f'MESSAGE: Error with getting updated ferry schedule from API. Using potentially outdated cache.'
            )

    return sched


def try_ferry_sched_request_all(ferry_cache):
    schedule = {
        'terminal 0': {
            'route 0': try_ferry_sched_request(0, 0, ferry_cache),
            'route 1': try_ferry_sched_request(0, 1, ferry_cache),
        },
        'terminal 1': {
            'route 0': try_ferry_sched_request(1, 0, ferry_cache),
            'route 1': try_ferry_sched_request(1, 1, ferry_cache),
        },
    }
    return schedule


def get_ferry_data():
    """Handles fetching and caching ferry data from API, and uses cached data when cache is already up-to-date.
Returns ferry data as dictionary. Returns 'error' if unable to get data from API and cache."""

    try:
        cache_flush_timestamp = int(get_ferry_cache_flush_timestamp())
    except:
        cache_flush_timestamp = math.inf
        admin_alert_thread(
            'Web App - ERROR',
            f'SoundX\nError at get_ferry_cache_flush_timestamp().\n'
            f'MESSAGE: Could not get cache_flush_timestamp from API. Assuming cache should be updated...'
        )

    with open('ferrycache.json', 'r') as file:
        json_data = json.load(file)

    ferry_cache_valid = validate_ferry_cache(json_data)

    ferry_dict = {}

    ferry_sched_source = 'new'  # Will be changed below to 'cache' if updated data from API is not required.

    if ferry_cache_valid:

        if json_data['cache timestamp'] > cache_flush_timestamp:
            # All cache is up-to-date.

            if json_data['alerts'][0]['RouteAlertText'] != "There was a problem retrieving ferry alerts from WSDOT.":
                # Cache for ferry alerts is usable.
                return json_data
            # Else: cache for ferry alerts is empty.

            ferry_sched_source = 'cache'
        # Else: cache is outdated.

    else:  # Cache is not valid.
        admin_alert_thread(
            'Web App - ERROR',
            f'SoundX\nError at validate_ferry_cache().\n'
            f'MESSAGE: Ferry cache json not validated. Possibly corrupt.'
        )

    ferry_dict['cache timestamp'] = int(time.time())  # Changed to 0 below if unable to update all ferry data.

    alerts_result = try_ferry_alert_request(json_data)

    if alerts_result['source'] == 'error':
        ferry_dict['cache timestamp'] = 0
        ferry_dict['alerts'] = {
            'RouteAlertText': 'There was a problem retrieving ferry alerts from WSDOT.',
            'BulletinText': '',
        }
        # Testing for exact string in RouteAlertText above in prior code. Must change both!
        admin_alert_thread(
            'Web App - ERROR',
            f'SoundX\nError at try_ferry_alert_request().\n'
            f'MESSAGE: There was a problem retrieving ferry alerts from WSDOT as well as from cache.'
        )

    else:  # alerts_result['source'] == 'cache' or 'new'
        ferry_dict['alerts'] = alerts_result['data']
        if alerts_result['source'] == 'cache':
            ferry_dict['cache timestamp'] = 0
            admin_alert_thread(
                'Web App - ERROR',
                f'SoundX\nError at try_ferry_alert_request().\n'
                f'MESSAGE: There was a problem retrieving ferry alerts from WSDOT. Using possibly outdated cache.'
            )

    if ferry_sched_source == 'cache':
        ferry_dict['schedules'] = json_data['schedules']

    else:  # ferry_sched_source == 'new'

        schedules = try_ferry_sched_request_all(json_data)
        ferry_dict['schedules'] = {}

        for terminal in schedules:
            ferry_dict['schedules'][terminal] = {}
            for route in schedules[terminal]:
                if schedules[terminal][route]['source'] == 'error':
                    ferry_dict['cache timestamp'] = 0
                    ferry_dict['schedules'][terminal][route] = []
                else:  # schedules[terminal][route]['source'] == 'cache' or 'new'
                    ferry_dict['schedules'][terminal][route] = schedules[terminal][route]['data']
                    if schedules[terminal][route]['source'] == 'cache':
                        ferry_dict['cache timestamp'] = 0

    with open('ferrycache.json', 'w') as file:
        json.dump(ferry_dict, file, indent=4)

    return ferry_dict


def soonest_ferry_depart_timestamp(drive_begin_timestamp, drive_secs, ferry_schedule):
    """Input ferry_schedule as a list of departure timestamps."""

    earliest_arrive_at_ferry_timestamp = drive_begin_timestamp + drive_secs + 300  # Add a 5-minute cushion
    departure_list_spare_time = []
    for departure in ferry_schedule:
        spare_time = (departure - earliest_arrive_at_ferry_timestamp) % 86400
        # If spare time is negative, it's made positive with modulo 86400 seconds per day.
        departure_list_spare_time.append(spare_time)
    if len(departure_list_spare_time) == 0:
        return 10000000000
    lowest_spare_time = min(departure_list_spare_time)

    # Returning future timestamp even if using old cache.
    return earliest_arrive_at_ferry_timestamp + lowest_spare_time


def get_route_info(depart_timestamp, origin, route, terminal, ferry_schedule, destination):
    """Output is dictionary. Keys: arrive timestamp, arrive formatted time, drive seconds to ferry,
    drive minutes to ferry, ferry departure timestamp, ferry departure formatted time, leave in x minutes,
    drive start timestamp, route number, terminal number, terminal name, string"""

    depart_term_addr = FERRY_ROUTES[route]["terminals"][terminal]["address"]
    drive_secs_to_ferry = get_drive_secs(depart_timestamp=depart_timestamp, origin=origin,
                                         destination=depart_term_addr, traffic_model="pessimistic")
    if drive_secs_to_ferry == "error":
        return "error"
    ferry_depart_timestamp = soonest_ferry_depart_timestamp(drive_begin_timestamp=depart_timestamp,
                                                            drive_secs=drive_secs_to_ferry,
                                                            ferry_schedule=ferry_schedule)
    ferry_arrive_timestamp = ferry_depart_timestamp + FERRY_ROUTES[route]["crossing minutes"] * 60
    arrive_term_addr = FERRY_ROUTES[route]["terminals"][terminal * -1 + 1]["address"]

    drive_secs_from_ferry = get_drive_secs(depart_timestamp=ferry_arrive_timestamp, origin=arrive_term_addr,
                                           destination=destination, traffic_model="best_guess")
    if drive_secs_from_ferry == "error":
        return "error"

    arrive_timestamp = ferry_arrive_timestamp + drive_secs_from_ferry

    data = {
        "arrive timestamp": arrive_timestamp,
        "arrive formatted time": format_timestamp(arrive_timestamp),
        "drive seconds to ferry": drive_secs_to_ferry,
        "drive minutes to ferry": int(round(number=(drive_secs_to_ferry / 60), ndigits=0)),
        "ferry departure timestamp": ferry_depart_timestamp,
        "ferry departure formatted time": format_timestamp(ferry_depart_timestamp),
        "leave in x minutes": int(
            round(number=((ferry_depart_timestamp - time.time() - drive_secs_to_ferry) / 60), ndigits=0)),
        "drive start timestamp": ferry_depart_timestamp - drive_secs_to_ferry,
        "route number": route,
        "terminal number": terminal,
        "terminal name": FERRY_ROUTES[route]["terminals"][terminal]["name"],
    }

    data['html'] = f'''
<h3>VIA THE {data["terminal name"].upper()} FERRY TERMINAL:</h3>
<table>
    <tr>
        <td class="table-col-left">DEPART ORIGIN:</td>
        <td class="table-col-right">{format_timestamp(data["drive start timestamp"])} <span>(in {data["leave in x minutes"]} minutes)</span></td>
    </tr>
    <tr>
        <td class="table-col-left">DRIVE TO FERRY:</td>
        <td class="table-col-right">{data["drive minutes to ferry"]} minutes</td>
    </tr>
    <tr>
        <td class="table-col-left">FERRY DEPARTURE:</td>
        <td class="table-col-right">{data["ferry departure formatted time"]}</td>
    </tr>
    <tr>
        <td class="table-col-left">FERRY CROSSING TIME:</td>
        <td class="table-col-right">{FERRY_ROUTES[route]["crossing minutes"]} minutes</td>
    </tr>
    <tr>
        <td class="table-col-left">DRIVE FROM FERRY:</td>
        <td class="table-col-right">{int(round(number=(drive_secs_from_ferry / 60), ndigits=0))} minutes</td>
    </tr>
    <tr>
        <td class="table-col-left"><strong>TOTAL TRAVEL TIME:</strong></td>
        <td class="table-col-right"><strong>{round((data["arrive timestamp"] - data["drive start timestamp"]) / 60)} minutes</strong></td>
    </tr>
    <tr>
        <td class="table-col-left white"><strong>FINAL DESTINATION:</strong></td>
        <td class="table-col-right white"><strong>{data["arrive formatted time"]}</strong></td>
    </tr>
</table>'''

    return data


def format_timestamp(timestamp):  # Example: 09:35 AM
    pacific_tz = timezone("US/Pacific")
    time_to_format = datetime.fromtimestamp(timestamp, tz=pacific_tz)
    return time_to_format.strftime("%I:%M %p")


def check_route_coords(origin, destination):
    """Returns dictionary with 'status' key.
If 'status' is 'ok', other keys are 'origin coords', 'destination coords', and 'depart terminal'.
If 'status' is 'error', includes 'message' key containing error message."""

    origin_coords = get_coords(origin)
    if origin_coords == "error":
        return {'status': 'error', 'message': "There was a problem retrieving location data for your origin "
                                              "within Kitsap, King, or Snohomish counties. Please adjust "
                                              "what was entered for your origin and try again."}

    destination_coords = get_coords(destination)
    if destination_coords == "error":
        return {'status': 'error', 'message': "There was a problem retrieving location data for your destination "
                                              "within Kitsap, King, or Snohomish counties. Please adjust "
                                              "what was entered for your destination and try again."}

    origin_east = origin_coords["county"] == "King County" or origin_coords["county"] == "Snohomish County"
    origin_valid = origin_east or origin_coords["county"] == "Kitsap County"
    destination_valid = \
        destination_coords["county"] == "King County" or destination_coords["county"] == "Snohomish County"

    if origin_east:
        if destination_valid:
            return {'status': 'error', 'message': "One of the locations should be in Kitsap County. "
                                                  "Please adjust what you entered for this location."}
        else:
            destination_valid = destination_coords["county"] == "Kitsap County"
    elif destination_coords["county"] == "Kitsap County":
        return {'status': 'error', 'message': "One of the locations should be in King or Snohomish County. "
                                              "Please adjust what you entered for this location."}

    if not origin_valid:
        return {'status': 'error',
                'message': "Sorry, but I didn't find your origin within Kitsap, King, or Snohomish counties. "
                           "Maybe try entering something more specific."}
    elif not destination_valid:
        return {'status': 'error',
                'message': "Sorry, but I didn't find your destination within Kitsap, King, or Snohomish counties. "
                           "Maybe try entering something more specific."}

    depart_terminal = 1
    if origin_east:
        depart_terminal = 0

    origin_coords = f"{origin_coords['lat']},{origin_coords['long']}"
    destination_coords = f"{destination_coords['lat']},{destination_coords['long']}"

    result = {
        'status': 'ok',
        'origin coords': origin_coords,
        'destination coords': destination_coords,
        'depart terminal': depart_terminal,
    }

    return result


def get_info_all_routes(origin, destination, depart_terminal, ferry_schedule):
    timestamp_now = time.time()  # now

    all_routes_info = []

    for route_num in range(2):
        this_route_info = \
            get_route_info(
                depart_timestamp=timestamp_now, origin=origin, route=route_num, terminal=depart_terminal,
                ferry_schedule=ferry_schedule[f'terminal {depart_terminal}'][f'route {route_num}'],
                destination=destination
            )

        if this_route_info == "error":
            return "error"

        if this_route_info['arrive timestamp'] - time.time() < 86400:  # Arriving less than 24 hours from now.
            all_routes_info.append(this_route_info)

    route_2_drive_secs = get_drive_secs(
        depart_timestamp=timestamp_now, origin=origin, destination=destination, traffic_model="best_guess"
    )

    if route_2_drive_secs == "error":
        return "error"

    if route_2_drive_secs < 86400:  # Arriving less than 24 hours from now.

        route_2_html = f'''
<h3>VIA THE TACOMA NARROWS BRIDGE:<br><span>(no ferry)</span></h3>
<table>
    <tr>
        <td class="table-col-left">DEPART ORIGIN:</td>
        <td class="table-col-right">Now</td>
    </tr>
    <tr>
        <td class="table-col-left"><strong>TOTAL TRAVEL TIME:</strong></td>
        <td class="table-col-right"><strong>{round(route_2_drive_secs / 60)} minutes</strong></td>
    </tr>
    <tr>
        <td class="table-col-left white"><strong>FINAL DESTINATION:</strong></td>
        <td class="table-col-right white"><strong>{format_timestamp(route_2_drive_secs + timestamp_now)}</strong></td>
    </tr>
</table>'''

        all_routes_info.append({
            'drive secs': route_2_drive_secs,
            'arrive timestamp': route_2_drive_secs + timestamp_now,
            'html': route_2_html
        })

    sorted_routes_info = sorted(all_routes_info, key=lambda route: route['arrive timestamp'])

    sorted_routes_html = []
    for route_info in sorted_routes_info:
        sorted_routes_html.append(route_info['html'])

    return sorted_routes_html
