release: make clean compile rollup schema
web: gunicorn --pythonpath src code:application
init_db: python src/initialize.py
