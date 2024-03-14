# helptext: MAKEFILE HELPTEXT
# helptext:

# helptext: setup:
# helptext:
# helptext: Set up the project for development
# helptext:
# helptext:
.PHONY: setup
setup:
	@./scripts/$@

# helptext: run:
# helptext:
# helptext: Run the project locally
# helptext:
# helptext:
.PHONY: run
run: setup build
	@./scripts/$@

# helptext: clean:
# helptext:
# helptext: Clean the project
# helptext:
# helptext:
.PHONY: clean
clean:
	@./scripts/$@

# helptext: format:
# helptext:
# helptext: Format the code, tests, and anything else that needs formatting in a project
# helptext:
# helptext:
.PHONY: format
format:
	@./scripts/$@

# helptext: unittest:
# helptext:
# helptext: Run the test suit for the project
# helptext:
# helptext:
.PHONY: unittest
unittest:
	@echo ""
	@echo "====================================================================="
	@echo "Run Unit Tests"
	@echo "====================================================================="
	@echo ""
	@./scripts/$@

# helptext: coverage:
# helptext:
# helptext: Run code coverage reports
# helptext:
# helptext:
.PHONY: coverage
coverage:
	@echo ""
	@echo "====================================================================="
	@echo "Check Test Coverage"
	@echo "====================================================================="
	@echo ""
	@./scripts/$@

# helptext: lint:
# helptext:
# helptext: Static code analysis for the project
# helptext:
# helptext:
.PHONY: lint
lint:
	@echo ""
	@echo "====================================================================="
	@echo "Run Linter"
	@echo "====================================================================="
	@echo ""
	@./scripts/$@

# helptext: test:
# helptext:
# helptext: Combine unit tests, coverage reports, etc
# helptext:
# helptext:
.PHONY: test
test: setup unittest coverage lint

# helptext: build:
# helptext:
# helptext: Build a container from the current directory's code
# helptext:
# helptext:
.PHONY: build
build:
	@./scripts/$@

# helptext: publish:
# helptext:
# helptext: Publish the last built container
# helptext:
# helptext:
.PHONY: publish
publish:
	@./scripts/$@

# helptext: preprod-deploy:
# helptext:
# helptext: Deploy to the preprod env (make sure that `make clean` is ran right before
# helptext: the script)
# helptext:
# helptext:
.PHONY: preprod-deploy
preprod-deploy:
	make clean
	@./scripts/$@

# helptext: prod-deploy:
# helptext:
# helptext: Deploy to the prod env (make sure that `make clean` is ran right before the
# helptext: script)
# helptext:
# helptext:
.PHONY: prod-deploy
prod-deploy:
	make clean
	@./scripts/$@

# helptext: view-local-logs:
# helptext:
# helptext: View the logs from `make run`
# helptext:
# helptext:
.PHONY: view-local-logs
view-local-logs:
	@./scripts/$@

# helptext: view-preprod-logs:
# helptext:
# helptext: View the logs in preprod whether in the terminal or opening up a browser
# helptext: window to splunk or the location where the logs can be found.
# helptext:
# helptext:
.PHONY: view-preprod-logs
view-preprod-logs:
	@./scripts/$@

# helptext: view-prod-logs:
# helptext:
# helptext: View the logs in prod whether in the terminal or opening up a browser
# helptext: window to splunk or the location where the logs can be found.
# helptext:
# helptext:
.PHONY: view-prod-logs
view-prod-logs:
	@./scripts/$@

# helptext: security-report
# helptext:
# helptext: Search for issues with the dependencies and generate a report
# helptext:
# helptext:
.PHONY: security-report
security-report:
	@./scripts/$@

# helptext: help:
# helptext:
# helptext: View the helptext in the makefile
# helptext:
# helptext:
.PHONY: help
help:
	@grep '^# helptext:' Makefile |  sed 's/.*helptext://' | less
