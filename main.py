from flask import Flask, Response, render_template, request, url_for, redirect
import ferry as ferry_mod


# Copyright 2021 Johnathan Pennington | All rights reserved.


app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith(url_for('harmonizer')):
        message_body = f'HARMio\n404 Redirect\n{request.url}\nPage not found. Rendered harmonizer.html.'
        ferry_mod.admin_alert_thread('Web App - ERROR', message_body)
        return render_template('harmonizer.html'), 404
    if request.path.startswith(url_for('volatile3gons')):
        message_body = f'Volatile3gons\n404 Redirect\n{request.url}\nPage not found. Rendered volatile3gons.html.'
        ferry_mod.admin_alert_thread('Web App - ERROR', message_body)
        return render_template('volatile3gons.html'), 404
    if request.path.startswith(url_for('ferry')):
        message_body = f'SoundX\n404 Redirect\n{request.url}\nPage not found. Ran ferry_mod.render_home_template().'
        ferry_mod.admin_alert_thread('Web App - ERROR', message_body)
        return ferry_mod.render_home_template(), 404
    if not request.path.startswith('/favicon') and not request.path.startswith('/robots'):
        message_body = f'Portfolio Page\n404 Redirect\n{request.url}\nPage not found. Rendered index.html.'
        ferry_mod.admin_alert_thread('Web App - ERROR', message_body)
        return render_template('index.html'), 404


@app.route('/serverterminal', methods=['POST'])
def server_terminal():
    if request.method == 'POST':
        if 'appname' not in request.form or 'userstartmsec' not in request.form or 'usersecs' not in request.form:
            message_list = ['Bad request to server_terminal.', 'POST arguments below.']
            for item in request.form:
                message_line = f'{item}: {request.form[item]}'
                message_list.append(message_line)
            message = '\n'.join(message_list)
            ferry_mod.admin_alert_thread('Web App - ERROR', message)
            return Response(status=400)
        app_name = request.form['appname']
        user_start_msec = request.form['userstartmsec']
        user_secs = request.form['usersecs']
        message = f'{app_name}\nUser Time Log\nUser timestamp id: {user_start_msec}\n' \
                  f'User duration: {user_secs} seconds'
        ferry_mod.admin_alert_thread('Web App - Log', message)
        return Response(status=200)


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/qr')
def qr():
    return redirect(url_for('home'))


@app.route('/harmio')
def harmonizer():
    return render_template('harmonizer.html')


@app.route('/volatile3gons')
def volatile3gons():
    return render_template('volatile3gons.html')


@app.route('/soundx')
def ferry():
    return ferry_mod.render_home_template()


@app.route('/soundx/query')
def ferry_query():
    if 'origin' in request.args:
        origin = request.args['origin']
    else:
        origin = ''
    if 'destination' in request.args:
        destination = request.args['destination']
    else:
        destination = ''
    return ferry_mod.render_results_template(origin, destination)


if __name__ == '__main__':
    app.run()
