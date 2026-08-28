"""The site's pages: public URL -> (template file, database page_slug).

This is the one place that knows the page list. config.urls routes and renders
from it, and the scripts in tools/ read it so they can never drift from what is
actually served. Adding a page means adding a line here.
"""

PAGES = {
    "": ("index.html", "home"),
    "contact": ("pages/contact.html", "contact"),
    "insights": ("pages/insights.html", "insights"),
    "sectors": ("pages/sectors.html", "sectors"),
    "about/leadership": ("pages/about/leadership.html", "leadership"),
    "about/our-approach": ("pages/about/our-approach.html", "our_approach"),
    "about/global-presence": ("pages/about/global-presence.html", "global_presence"),
    "about/vision-mission": ("pages/about/vision-mission.html", "vision_mission"),
    "expertise": ("pages/expertise/index.html", "expertise"),
    "expertise/project-management": (
        "pages/expertise/project-management.html",
        "project_management",
    ),
    "expertise/consulting-engineering": (
        "pages/expertise/consulting-engineering.html",
        "consulting_engineering",
    ),
    "expertise/design": ("pages/expertise/design.html", "design"),
    "expertise/cost-management": (
        "pages/expertise/cost-management.html",
        "cost_management",
    ),
    "expertise/cost-management-2": (
        "pages/expertise/cost-management-2.html",
        "cost_management2",
    ),
    "expertise/post-contract": (
        "pages/expertise/post-contract.html",
        "post_contract",
    ),
    "expertise/tender-management": (
        "pages/expertise/tender-management.html",
        "tender-management",
    ),
    "expertise/value-engineering": (
        "pages/expertise/value-engineering.html",
        "value_engineering",
    ),
    "expertise/schedule-management": (
        "pages/expertise/schedule-management.html",
        "schedule_management",
    ),
    "expertise/construction-project": (
        "pages/expertise/construction-project.html",
        "construction_project",
    ),
    "expertise/contracts-arbitration": (
        "pages/expertise/contracts-arbitration.html",
        "contracts_arbitration",
    ),
}

# Convenience views of the same data.
TEMPLATE_FOR_URL = {url: template for url, (template, _) in PAGES.items()}
SLUG_FOR_URL = {url: slug for url, (_, slug) in PAGES.items()}
SLUG_FOR_TEMPLATE = {template: slug for template, slug in PAGES.values()}
URL_FOR_TEMPLATE = {template: url for url, (template, _) in PAGES.items()}
