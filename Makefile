# Makefile -- real, repeatable *.tcos.us -> lab.tcos.us deploy process.
#
# Real trigger (2026-08-28): the first real Step 1 clone deploy
# (tcos-www + resume/blog onto lab.tcos.us) was done entirely by hand
# -- tar/scp/pct push, a missed css/js asset dir, a missed clean-URL
# link fix. Spencer, direct: "should be a repeatable process... a
# makefile would be easy to segregate." One real target per site,
# `make lab` runs all of them; `make release` is named but honestly
# NOT implemented yet -- Step 3 of the plan (fleet-ops#295), not this
# session's scope.
#
# Real infra touched: the `view` container (pve vmid 107, real webroot
# /www/*) via `pct push`. Source repos are real sibling checkouts
# under $(HOME)/git/ -- never hardcode a real username's home path
# here (HEE Policy, PROMPTING_RULES.md rule 10).

TCOS_WWW := $(HOME)/git/tcos-www
RESUME   := $(HOME)/git/resume
VIEW_VMID := 107

.PHONY: help lab lab-tcos-www lab-blog lab-old-commits lab-tree-index lab-verify release

help:
	@echo "make targets (this repo's lab helpers for view.lab):"
	@echo "  help             this list"
	@echo "  lab              lab-verify (the site deploys moved, see below)"
	@echo "  lab-verify       status codes of lab.tcos.us and the blog host"
	@echo "  lab-old-commits  build and push view.lab's old-commits.html (LOCAL=ndjson optional)"
	@echo "  lab-tree-index   build and push view.lab's files/ and diffs/ indexes"
	@echo "  lab-tcos-www     RETIRED: tcos-www CI payload + lab-pull; tcos-www ./deploy.sh lab"
	@echo "  lab-blog         RETIRED: resume bin/deploy-pages.sh lab (rsync into the share)"
	@echo "  release          not implemented (fleet-ops#295)"

lab: lab-verify

# lab-tcos-www and lab-blog are RETIRED (2026-10-01). Both pushed over
# `ssh pve` + `pct push` into ct107, whose /www is pve's share now, owned
# 1000:1005, which container root cannot write; and the fleet does not ssh to
# pve for a lab deploy (fleet-ops ticket 0148). Their replacements:
#   tcos-www  CI publishes a payload (this repo's bin/lab_link_transform.py is
#             still the transform); lab-pull installs it (fleet-ops#928);
#             tcos-www's ./deploy.sh lab waits for it.
#   resume    bin/deploy-pages.sh lab rsyncs dist/ into the lab share
#             (resume#116), the same path as media/bin/deploy.sh.
# The targets stay, failing loudly, so a muscle-memory `make lab` says where
# the work went instead of hanging on an ssh prompt.
lab-tcos-www:
	@echo "lab-tcos-www: retired -- tcos-www's CI publishes a payload and lab-pull installs it; run ./deploy.sh lab in tcos-www to wait for it" >&2
	@exit 1

# tcos.app has no target here on purpose: its lab surface (app.lab.tcos.us) is
# installed by lab-pull on pve from tcos-app's own release, with no ssh and no
# hand-push. See fleet-ops pve/lab-deploy/README.md.

lab-blog:
	@echo "lab-blog: retired -- resume's bin/deploy-pages.sh lab rsyncs dist/ into the lab share" >&2
	@exit 1

# Real, honest post-deploy check -- not a substitute for hee-view
# --sites (which reads SITEMAP.yaml), just a fast sanity pass on the
# two real targets this Makefile itself just touched.
# old-commits.html -- every non-main branch on origin across the org, with
# a cleanup verdict each (.github#84). `collect` needs the org checkouts
# under $(HOME)/git and gh auth; `render` needs only the JSON. LOCAL is an
# optional ndjson from `hee repo-refresh hygiene --json` run on another
# machine (the laptop), merged in as "laptop-local only" rows.
OLD_COMMITS_JSON ?= /tmp/old-commits.json
LOCAL ?=
lab-old-commits:
	bin/render-old-commits.py collect --out $(OLD_COMMITS_JSON)
	HEE_BRANDING=$${HEE_BRANDING:-$(HOME)/git/tcos-audit/policy/branding.card.v1.yaml} \
		bin/render-old-commits.py render $(OLD_COMMITS_JSON) $(if $(LOCAL),--local $(LOCAL),) --out /tmp/lab-deploy-old-commits
	scp /tmp/lab-deploy-old-commits/old-commits.html pve:/tmp/old-commits.html
	ssh pve "pct push $(VIEW_VMID) /tmp/old-commits.html /www/old-commits.html"
	@echo "view.lab.tcos.us/old-commits.html: $$(curl -s -o /dev/null -w '%{http_code}' https://view.lab.tcos.us/old-commits.html)"

# files/index.html and diffs/index.html -- busybox httpd lists no
# directories, so the two trees review runs write to the view container
# answered 404 at their roots while every page under them was live
# (hee view --crawl, 2026-09-06). Built from what the container holds.
TREE_JSON ?= /tmp/view-tree.json
lab-tree-index:
	bin/render-tree-index.py collect --out $(TREE_JSON)
	HEE_BRANDING=$${HEE_BRANDING:-$(HOME)/git/tcos-audit/policy/branding.card.v1.yaml} \
		bin/render-tree-index.py render $(TREE_JSON) --out /tmp/lab-deploy-tree-index
	scp -q /tmp/lab-deploy-tree-index/files/index.html pve:/tmp/files-index.html
	scp -q /tmp/lab-deploy-tree-index/diffs/index.html pve:/tmp/diffs-index.html
	ssh pve "pct push $(VIEW_VMID) /tmp/files-index.html /www/files/index.html && pct push $(VIEW_VMID) /tmp/diffs-index.html /www/diffs/index.html"
	@echo "view.lab.tcos.us/files/: $$(curl -s -o /dev/null -w '%{http_code}' https://view.lab.tcos.us/files/)"
	@echo "view.lab.tcos.us/diffs/: $$(curl -s -o /dev/null -w '%{http_code}' https://view.lab.tcos.us/diffs/)"

lab-verify:
	@echo "lab.tcos.us:               $$(curl -s -o /dev/null -w '%{http_code}' https://lab.tcos.us/)"
	@echo "lab.tcos.us/css/site.css:  $$(curl -s -o /dev/null -w '%{http_code}' https://lab.tcos.us/css/site.css)"
	@echo "spencer.blog.lab.tcos.us:  $$(curl -s -o /dev/null -w '%{http_code}' https://spencer.blog.lab.tcos.us/)"

# Real Step 3 of the *.tcos.us -> lab.tcos.us plan (lab -> prod
# promotion: deny-all/allow-select filter, real git tags, a real
# major/minor scheme) -- NOT built yet. This target exists so the real
# shape of the process is visible, but it fails loudly rather than
# pretending to do something -- no half-finished implementations.
#
# Real known future dependency, Spencer direct (2026-08-28): prod
# (*.tcos.us) currently routes through Cloudflare Pages/Workers, not
# haproxy -- lab.tcos.us's real ACL+backend+path-rewrite routing
# (this Makefile's actual deploy mechanism) has no equivalent on the
# live side yet. For `release` to give lab and prod the *same*
# real routing function, live will need its own real haproxy
# deployment (or an equivalent) before this target can be built for
# real -- not scoped this session, noted here so it isn't lost.
release:
	@echo "release: not yet implemented -- see fleet-ops#295 (Step 3, not scoped this session)" >&2
	@exit 1
