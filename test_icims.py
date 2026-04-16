#!/usr/bin/env python3
import os
import sys
import django
import importlib.util

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DSCovery.settings')
django.setup()

from django.conf import settings

# Test basic import - note: to-do is a directory, not a package for imports
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("icims_module", "/Users/timbaxter/Development/DSCovery/jobsearch/importers/to-do/icims.py")
    icims_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(icims_module)
    print("✓ Module imports successfully")
except Exception as e:
    print(f"✗ Failed to import module: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check firms structure
print(f"\n✓ Found {len(icims_module.firms)} companies")
for company, url in icims_module.firms:
    print(f"  - {company}")

# Try to get_jobs
try:
    print("\nFetching jobs...")
    jobs = icims_module.get_jobs()
    print(f"\n✓ get_jobs() executed successfully")
    print(f"  Returned {len(jobs)} jobs total")
    
    if jobs:
        print(f"\nSample job data (first 2):")
        for job in jobs[:2]:
            print(f"\n  Company: {job['company']}")
            print(f"  Title: {job['title']}")
            print(f"  Location: {job['location']}")
            print(f"  Job ID: {job['job_id']}")
            print(f"  Posted: {job['pub_date']}")
            print(f"  Link: {job['link'][:70]}{'...' if len(job['link']) > 70 else ''}")
    else:
        print("  No jobs were returned")
except Exception as e:
    print(f"\n✗ Error running get_jobs(): {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
