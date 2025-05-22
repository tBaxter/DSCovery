import importlib

# Names of each importer module (match the filenames in this folder)
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
    For each module name in IMPORTERS, dynamically import 
    jobsearch.importers.<name> and call its get_jobs().
    """
    all_jobs = []
    for name in IMPORTERS:
        module = importlib.import_module(f"jobsearch.importers.{name}")
        batch = getattr(module, "get_jobs", lambda: [])() or []
        all_jobs.extend(batch)
    return all_jobs