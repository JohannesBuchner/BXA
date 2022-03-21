# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = 
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = bxa
SOURCEDIR     = .
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

reset-gh-pages:
	rm -rf build/html/
	git worktree prune
	git worktree add build/html/ gh-pages
	git worktree list

update-gh-pages:
	rm -rf build/html/.buildinfo build/html/*
	$(MAKE) html
	git -C build/html add .
	git -C build/html commit -av -m 'update doc'


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	cp ../examples/xspec/reference-output/*.pdf .
	cp ../examples/xspec/reference-output/*.png .
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
