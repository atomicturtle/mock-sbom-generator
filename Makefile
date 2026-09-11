# Makefile for Atomic BOM (mock-sbom-generator)

PREFIX ?= /usr
DESTDIR ?=
BINDIR ?= $(PREFIX)/bin
DATADIR ?= $(PREFIX)/share
MANDIR ?= $(DATADIR)/man
DOCDIR ?= $(DATADIR)/doc/mock-sbom-generator
PYTHON ?= python3
SITELIB ?= $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_path('purelib'))")

INSTALL ?= install

.PHONY: all help test install clean

all:
	@true

help:
	@echo "Targets:"
	@echo "  make        - No-op build (Python sources)"
	@echo "  make test   - Run unit tests"
	@echo "  make install - Install CLI, plugin, libraries, man, and docs"
	@echo "  make clean  - Remove bytecode and pytest cache"
	@echo "  make help   - Show this help"

test:
	python3 -m pytest tests/ -q

install:
	$(INSTALL) -d $(DESTDIR)$(BINDIR)
	$(INSTALL) -m 0755 SOURCES/mock-sbom-generator.py \
		$(DESTDIR)$(BINDIR)/mock-sbom-generator
	$(INSTALL) -d $(DESTDIR)$(SITELIB)/mockbuild/plugins
	$(INSTALL) -m 0644 SOURCES/plugins/sbom_generator.py \
		$(DESTDIR)$(SITELIB)/mockbuild/plugins/sbom_generator.py
	$(INSTALL) -m 0644 SOURCES/mockbuild/sbom_generate.py \
		$(DESTDIR)$(SITELIB)/mockbuild/sbom_generate.py
	$(INSTALL) -m 0644 SOURCES/mockbuild/sbom_utils.py \
		$(DESTDIR)$(SITELIB)/mockbuild/sbom_utils.py
	$(INSTALL) -m 0644 SOURCES/mockbuild/sbom_cyclonedx.py \
		$(DESTDIR)$(SITELIB)/mockbuild/sbom_cyclonedx.py
	$(INSTALL) -m 0644 SOURCES/mockbuild/sbom_spdx.py \
		$(DESTDIR)$(SITELIB)/mockbuild/sbom_spdx.py
	$(INSTALL) -d $(DESTDIR)$(MANDIR)/man1
	$(INSTALL) -m 0644 SOURCES/mock-sbom-generator.1 \
		$(DESTDIR)$(MANDIR)/man1/mock-sbom-generator.1
	$(INSTALL) -d $(DESTDIR)$(DOCDIR)
	$(INSTALL) -m 0644 SOURCES/Plugin-SBOM.md $(DESTDIR)$(DOCDIR)/Plugin-SBOM.md

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete
	rm -rf .pytest_cache
