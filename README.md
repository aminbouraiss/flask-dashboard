## Project description

A Flask application serving a React powered marketing dashboard. 
- This project contains the necessary files for a deployment to a Google App Engine instance.
- The source code of the React app is available [here](https://github.com/aminbouraiss/react-dashboard).

This dashboard template is adapted from the the Gentelella bootstrap admin template by [colorlib](https://colorlib.com/polygon/gentelella/index.html).

## Live Demo

Click [here](https://lively-welder-190307.appspot.com/) to see the dashboard in action.

## Installation

#### 1. (Optional) Set up a virtual environment
[Python official doc on virtual environments](https://docs.python.org/3/library/venv.html) 

#### 2. Get the code
```shell
$git clone https://github.com/aminbouraiss/flask-dashboard.git
$cd flask-dashboard
```    

#### 3. Install the project dependencies
```shell
$pip install -r requirements.txt
```
#### 4. Running the local server
Launch the dev server with the following commands:
```shell
$export FLASK_APP=flask_app.py
$export FLASK_DEBUG=1
$flask run
```
The local server will be available at:
**Local:**            http://localhost:3000/
**On Your Network:**  http://192.168.0.5:3000/

## Deployment to Google App engine

The full documentation is available [here](https://cloud.google.com/appengine/docs/standard/python/quickstart).

1. Create a new GCP project and App Engine application using the [GCP Console](https://console.cloud.google.com/projectselector/appengine/create?lang=python&st=true&_ga=2.96565727.1573023038.1514731330-1693154763.1416115773)
2. When prompted, select the region where you want your App Engine application located. After your App Engine application is created, the Dashboard opens.
3. Download and install the [Google Cloud SDK](https://cloud.google.com/appengine/docs/standard/python/download) and then initialize the gcloud tool.
4. go to the directory that contains project code.
5. Install the project requirements with the following command:
	```shell
	$pip install -t lib -r requirements.txt
	```
6. Test the application using the local development server (**dev_appserver.py**), which is included with the SDK. start the local development server with the following command:
	```shell
	$dev_appserver.py app.yaml
	```
7. Visit **http://localhost:8080/** in your web browser to view the app.
8. You can deploy the final version of the app with the following command:
	```shell
	$gcloud app deploy
	```










