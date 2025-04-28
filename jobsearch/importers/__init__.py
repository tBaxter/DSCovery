from jobsearch.importers import paylocity, greenhouse, lever, jobvite  # adjust based on your importers

def get_all_jobs():
    """
    Calls each importer in turn and collects their job dictionaries.
    """
    all_jobs = []
    for importer in [paylocity, greenhouse, lever, jobvite]:
        jobs = importer.get_jobs() or []
        all_jobs.extend(jobs)
    return all_jobs