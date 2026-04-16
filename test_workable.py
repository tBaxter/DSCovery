#!/usr/bin/env python3
import os
import sys
import django
import importlib.util

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DSCovery.settings')
django.setup()

from django.conf import settings

# Test workable importer
try:
    spec = importlib.util.spec_from_file_location("workable_module", "/Users/timbaxter/Development/DSCovery/jobsearch/importers/to-do/workable.py")
    workable_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(workable_module)
    print("✓ Module imports successfully")
except Exception as e:
    print(f"✗ Failed to import module: {e}")
    sys.exit(1)

# Check firms structure
print(f"\n✓ Found {len(workable_module.firms)} companies")
for company, key in workable_module.firms:
    print(f"  - {company}")

# Try to get_jobs
try:
    print("\nFetching jobs...")
    jobs = workable_module.get_jobs()
    print(f"\n✓ get_jobs() executed successfully")
    print(f"  Returned {len(jobs)} jobs total")
    
    # Group by company
    by_company = {}
    for job in jobs:
        company = job['company']
        by_company[company] = by_company.get(company, 0) + 1
    
    print(f"\nJobs by company:")
    for company, count in sorted(by_company.items()):
        print(f"  - {company}: {count} jobs")
    
    if jobs:
        print(f"\nSample job data (first 3):")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n  {i}. {job['title']} ({job['company']})")
            print(f"     Location: {job['location']}")
            print(f"     Job ID: {job['job_id']}")
            print(f"     Link: {job['link'][:70]}")
    else:
        print("  No jobs were returned")
except Exception as e:
    print(f"\n✗ Error running get_jobs(): {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
