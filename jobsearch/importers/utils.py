

def already_in_jobs(new_job, jobs):
    """
    Simple helper function to check if a similar-ish item is already in the list of jobs
    based on the company and job name.
    """
    return any(
        job['company'] == new_job['company'] and job['title'] == new_job['title']
        for job in jobs
    )