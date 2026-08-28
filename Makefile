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

.PHONY: lab lab-tcos-www lab-blog lab-verify release

lab: lab-tcos-www lab-blog lab-verify

# Real single-target deploy -- "make only this" -- package+transform
# tcos-www's static real pages (html + css/js/shell, the asset dirs
# missed on the very first hand-run of this process) and push them to
# the view container's real webroot.
lab-tcos-www:
	rm -rf /tmp/lab-deploy-tcos-www
	bin/lab_link_transform.py $(TCOS_WWW) /tmp/lab-deploy-tcos-www-src
	mkdir -p /tmp/lab-deploy-tcos-www
	cd /tmp/lab-deploy-tcos-www-src && tar -czf /tmp/lab-deploy-tcos-www/site.tar.gz \
		activity.html careers.html contact.html contracts.html index.html ir.html people.html story.html \
		css js shell
	scp /tmp/lab-deploy-tcos-www/site.tar.gz pve:/tmp/tcos-www-static.tar.gz
	ssh pve "pct push $(VIEW_VMID) /tmp/tcos-www-static.tar.gz /tmp/tcos-www-static.tar.gz && \
		pct exec $(VIEW_VMID) -- sh -c 'rm -rf /www/tcos-www && mkdir -p /www/tcos-www && tar -xzf /tmp/tcos-www-static.tar.gz -C /www/tcos-www'"
	rm -rf /tmp/lab-deploy-tcos-www-src /tmp/lab-deploy-tcos-www

# Real single-target deploy for resume's real blog output
# ($(RESUME)/dist/ -- the actual wrangler pages_build_output_dir).
lab-blog:
	rm -f /tmp/resume-blog-static.tar.gz
	cd $(RESUME)/dist && tar -czf /tmp/resume-blog-static.tar.gz .
	scp /tmp/resume-blog-static.tar.gz pve:/tmp/resume-blog-static.tar.gz
	ssh pve "pct push $(VIEW_VMID) /tmp/resume-blog-static.tar.gz /tmp/resume-blog-static.tar.gz && \
		pct exec $(VIEW_VMID) -- sh -c 'rm -rf /www/spencer-blog && mkdir -p /www/spencer-blog && tar -xzf /tmp/resume-blog-static.tar.gz -C /www/spencer-blog'"
	rm -f /tmp/resume-blog-static.tar.gz

# Real, honest post-deploy check -- not a substitute for hee-view
# --sites (which reads SITEMAP.yaml), just a fast sanity pass on the
# two real targets this Makefile itself just touched.
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
