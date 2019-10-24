TARGET = target
DOCSET_NAME = ocaml-unofficial
ORIGONAL_DOC_URL = https://caml.inria.fr/distrib/ocaml-4.09/ocaml-4.09-refman-html.tar.gz

ORIGINAL_DOC = files/ocaml-4.09-refman-html.tar.gz
TAR_NAME = $(TARGET)/ocaml-unofficial.tgz
ROOT = $(TARGET)/$(DOCSET_NAME).docset
RESOURCES = $(ROOT)/Contents/Resources
CONTENTS = $(RESOURCES)/Documents

all: docset $(TAR_NAME)
docset: mkindex extra-files

$(CONTENTS):
	mkdir -p $@

download: $(ORIGINAL_DOC)

$(ORIGINAL_DOC):
	mkdir -p files
	curl -L -o "$@" "$(ORIGONAL_DOC_URL)"

extract: $(ORIGINAL_DOC)
	mkdir -p $(TARGET)/source
	tar xf $(ORIGINAL_DOC) -C $(TARGET)/source

copy: extract $(CONTENTS)
	mkdir -p $(CONTENTS)
	cp -a $(TARGET)/source/htmlman $(CONTENTS)

mkindex: copy
	pipenv run ./mkindex.py $(TARGET)/source $(RESOURCES)

$(TAR_NAME): docset
	tar --exclude=.DS_Store -czf $@ -C $(TARGET) $(DOCSET_NAME).docset

extra-files:
	cp Info.plist $(ROOT)/Contents/

clean-target:
	rm -rf $(TARGET)

clean: clean-target
	@echo "Removing only generated files"
	@echo "Run 'make clean-all' to remove downloaded files as well."

clean-all: clean-target
	rm -rf files

.PHONY: all clean clean-all clean-target copy docset download extra-files extract mkindex
