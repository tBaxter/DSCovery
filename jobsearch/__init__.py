import importlib

# List your importer module names (filenames without .py)
IMPORTERS = [
    "paylocity",
    "greenhouse_embedded",
    "lever",
    "jobvite",
    "mediabarn",
    "ad_hoc",
    "inroads",
    "bracari",
    "archesys",
    "applytojob",
    "ashby",
]

def get_all_jobs():
    """
    Dynamically import each scraper module, call its .get_jobs(), 
    and return the combined list of all jobs.
    """
    all_jobs = []
    for name in IMPORTERS:
        module = importlib.import_module(f"jobsearch.importers.{name}")
        batch = getattr(module, "get_jobs", lambda: [])() or []
        all_jobs.extend(batch)
    return all_jobs