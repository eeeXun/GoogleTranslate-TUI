DESTDIR = $(HOME)/.local/bin
CONFIGDIR = $(HOME)/.config/pylate

all:
	@echo Run \"make install\"

install:
	mkdir -p $(DESTDIR)
	cp pylate.py $(DESTDIR)/pylate
	mkdir -p $(CONFIGDIR)
	cp config.json $(CONFIGDIR)
	cp LanguageCode.csv $(CONFIGDIR)

uninstall:
	rm $(DESTDIR)/pylate
	rm -rf $(CONFIGDIR)
