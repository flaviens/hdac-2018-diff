.PHONY: diff
diff: | generated
	python3 diff.py

generated:
	mkdir -p $@

clean:
	rm -rf generated
