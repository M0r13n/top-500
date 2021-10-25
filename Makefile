install:
	gzip -d --keep res/packages.json.gz; \
	gzip -d --keep res/top-pypi-packages-30-days.json.gz; \
	python3 main.py

serve:
	python3 -m http.server
