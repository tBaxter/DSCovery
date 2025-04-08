Start-Process "powershell" -ArgumentList "docker run -p 6379:6379 redis" -WindowStyle Normal
Start-Process "powershell" -ArgumentList "pipenv run celery -A DSCovery worker -l info" -WindowStyle Normal
Start-Process "powershell" -ArgumentList "pipenv run celery -A DSCovery beat -l info" -WindowStyle Normal