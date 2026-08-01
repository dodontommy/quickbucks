.PHONY: all scrape serve clean

all: scrape

scrape:
	@echo "=== Running H1B Salary Data Scraper ==="
	python scraper.py
	@echo "=== Done ==="

serve:
	@echo "=== Starting dev server at http://localhost:8000 ==="
	@cd site && python3 -m http.server 8000

clean:
	@echo "=== Cleaning generated files ==="
	rm -rf data/*.csv
	rm -f site/sample_data.json
	@echo "=== Clean ==="