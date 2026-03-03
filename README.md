# DSCovery

DSCovery is a tool I created to find civic tech jobs with [Digital Services Coalition](http://digitalservicescoalition.org) firms. You can see it live at https://dscovery.fly.dev

It has importers for most common ATSs -- Greenhouse, Lever, Ashby, Paylocity, etc -- so adding additional companies is as simple as adding them to the list of companies using that ATS. We currently support more than 8 of the most common ATSs.

Additional importers will be added as there is demand, and pull requests are welcomed.

For DSCovery, we will also add DSC-adjacent firms, if they're good folks in the civic tech space. Please fill out a pull request if you know of a company we should add.


## Installing and running locally

1. Clone the repository and navigate to the project directory:
```
git clone https://github.com/tBaxter/DSCovery.git

cd DSCovery
```

2. Set up a virtual environment and install dependencies. We prefer to do this with pipenv:

```
# on a fresh mac or system Python you may see an "externally-managed-environment" error
# if you run `pip install pipenv`.  That means the OS-managed Python disallows
# modifying site-packages.  In that case either install pipenv with Homebrew or
# use the virtualenv approach below.

# install pipenv locally (user or brew avoids the restriction):
python3 -m pip install --user pipenv    # or use `brew install pipenv`

pipenv install
pipenv shell
```

If you prefer a traditional virtualenv or just want to avoid pipenv entirely, that's fine, too:
```
python -m venv venv  # (note: if you are not sure you're using python 3.1+ by default, you may want to change this command to python3 -m venv venv to be sure)
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
python manage.py runserver
```

5. (Optional) install Playwright browsers if you want to use the
   headless-browser importers for TeamTailor or Phenom People jobs:
```
pipenv run python -m playwright install
```

You should now be able to go to http://127.0.0.1:8000 to see the application running locally.


## Notes on importers

- The project dynamically loads `jobsearch/importers/*.py` modules.  Each
  importer may set a `PRIORITY` variable (default `0`) to influence the order
  they run; lower values execute first.  The new TeamTailor and Phenom
  importers set `PRIORITY = 10` so they run after all other importers, which
  helps avoid slowing down the core scrapers.
- TeamTailor and Phenom People sites render jobs in JavaScript.  The new
  `teamtailor.py` and `phenom.py` importers try a plain HTTP fetch, but if no
  job cards are found they fall back to launching a headless Playwright
  browser to render the page before scraping.  Make sure Playwright is
  installed if you plan to import companies using these platforms (e.g. Bixal,
  Fearless).
