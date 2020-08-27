import socket
import re
import json
import os
from crossdomain import *
from flask import Flask, render_template, url_for, request, Markup
from flask_script import Manager
from filterArray import generateValues, exportToJson

app = Flask(__name__)

manager = Manager(app)

# Generate the raw data
fileName = "data_source.csv"
filePath = os.path.join(os.path.curdir, 'data', fileName)
startData = generateValues(filePath)


# The hostname used to refresh the dashboard data
hostName = socket.gethostname()


@app.route('/')
def index():
    requestUrl = request.url
    protocol = (re.match("(https?)", requestUrl).groups()[0])
    xhrUrl = "{protocol}://{hostName}".format(
        protocol=protocol, hostName=hostName)
    xhrMarkup = Markup('<script>var xhrUrl ="{0}";</script>'.format(xhrUrl))
    return render_template('index.html', xhrMarkup=xhrMarkup)


@app.route('/chart')
@crossdomain(origin='*')
def getPlot():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    testStr = exportToJson(startData, startDate, endDate)
    return testStr


if __name__ == '__main__':
    manager.run()
