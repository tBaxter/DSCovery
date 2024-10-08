# DSCovery

DSCovery is a tool to find civic tech jobs with [Digital Services Coalition](http://digitalservicescoalition.org) firms. This is very much a work in progress, and I make no promises of stability.

You can see it live at https://dscovery.fly.dev

Additional importers will be added as there is demand, and pull requests are welcomed.

We will also add DSC-adjacent firms, if they're good folks in the civic tech space.


## Installing and running locally

1. Clone the repository and navigate to the project directory:
```
git clone https://github.com/tBaxter/DSCovery.git

cd DSCovery
```

2. Set up a virtual environment and install dependencies. We prefer to do this with pipenv:

```
pip install pipenv   # If you don't have it already
pipenv install
pipenv shell
```

If you prefer a traditional virtualenv, that's fine, too.
```
python -m venv venv  # (note: if you are not sure you're using python 3.1+ by default, you may want to change this command to python3 - m venv venv to be sure)
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

You should now be in a virtual environment, with dependencies installed.

3. Run Database Migrations:
```
python manage.py migrate
```

4. Start the development server
```
python manage.py migrate
```

You should now be able to go to http://127.0.0.1:8000 to see the application running locally.