if yours is broken/not working:

1) Install new dependencies: (up to date on 3/12/26)
   pip install Pillow
   pip install pyyaml
   (or pip install -r requirements.txt)s

2) In users/migrations/, delete everything except __init__.py  (eventually will have a .yaml for jobs too)

3) Delete db.sqlite3 from the project root

4) Rebuild the database:
   python manage.py makemigrations
   python manage.py migrate


finally
5) python manage.py loaddata sample_data/test_users.yaml
after you've loaded the test users
6) python manage.py loaddata sample_data/test_jobs.yaml
