# jobsearch/importers/__init__.py

from . import paylocity, greenhouse_embedded, lever, jobvite  # add any other importer modules here

def get_all_jobs():
    """
    Call each importer in turn, collect their outputs, and return one big list.
    """
    all_jobs = []
    for importer in (paylocity, greenhouse_embedded, lever, jobvite):
        jobs = importer.get_jobs() or []
        all_jobs.extend(jobs)
    return all_jobs