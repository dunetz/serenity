# all our targets are phony (no files to check).
.PHONY: help deploy

KUBECTL=microk8s.kubectl

help:
	@echo ''
	@echo 'Usage: make [TARGET] [EXTRA_ARGUMENTS]'
	@echo 'Targets:'
	@echo '  deploy    	deploy all Kubernetes YAML files'
	@echo ''

deploy:
	$(KUBECTL) delete jobs/sharadar-backfill
	$(KUBECTL) apply -f db/
	$(KUBECTL) apply -f feedhandlers/
	$(KUBECTL) apply -f mail/
	$(KUBECTL) apply -f research/
	$(KUBECTL) apply -f sharadar/
	$(KUBECTL) apply -f strategies/
