# Makefile for mock-sbom-generator sources

RPMBUILD_DIR := $(HOME)/rpmbuild
SOURCES_DIR := $(RPMBUILD_DIR)/SOURCES
SPECS_DIR := $(RPMBUILD_DIR)/SPECS
SRPMS_DIR := $(RPMBUILD_DIR)/SRPMS
RPMS_DIR := $(RPMBUILD_DIR)/RPMS

SPEC_FILE := mock-sbom-generator.spec

.PHONY: all clean distclean stage test rpmbuild-build help

all: help

help:
	@echo "Available targets:"
	@echo "  make test           - Run unit tests"
	@echo "  make rpmbuild-build - Build RPM using local rpmbuild"
	@echo "  make clean          - Clean rpmbuild directories"

stage:
	@mkdir -p $(RPMBUILD_DIR)/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	@./scripts/stage-rpm-sources.sh $(SOURCES_DIR)
	@cp $(SPEC_FILE) $(SPECS_DIR)/

test:
	python3 -m pytest tests/ -q

rpmbuild-build: stage
	@rpmbuild -ba $(SPECS_DIR)/$(SPEC_FILE) \
		--define "_sourcedir $(SOURCES_DIR)" \
		--define "_specdir $(SPECS_DIR)" \
		--define "_builddir $(RPMBUILD_DIR)/BUILD" \
		--define "_srcrpmdir $(SRPMS_DIR)" \
		--define "_rpmdir $(RPMS_DIR)"
	@echo "Build complete! RPMs are in: $(RPMS_DIR)/noarch/"
	@echo "SRPM is in: $(SRPMS_DIR)/"

clean:
	@rm -rf $(RPMBUILD_DIR)/BUILD/*
	@rm -rf $(RPMS_DIR)/noarch/*
	@rm -rf $(SRPMS_DIR)/*
	@echo "Clean complete!"

distclean: clean
	@rm -rf $(RPMBUILD_DIR)
	@echo "Distclean complete!"
