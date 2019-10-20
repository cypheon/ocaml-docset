ROOT=ocaml-unofficial.docset
CONTENTS=$(ROOT)/Contents/Resources/Documents
ORIGINAL_DOC=files/ocaml-4.09-refman-html.tar.gz
BUILD=_build

all: extract copy

$(CONTENTS):
	mkdir -p $@

extract:
	mkdir -p $(BUILD)/source
	tar xf $(ORIGINAL_DOC) -C $(BUILD)/source

copy: extract $(CONTENTS)
	cp -av $(BUILD)/source/htmlman/. $(CONTENTS)

.PHONY: extract
