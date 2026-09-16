"""The site's pages: public URL -> (template file, database page_slug).

This is the one place that knows the page list. config.urls routes and renders
from it, and the scripts in tools/ read it so they can never drift from what is
actually served. Adding a page means adding a line here.
"""

import json

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

SITE_NAME = "COREXION"
LOGO_PATH = "/assets/images/corexion_logo_transparent.png"

# Public URL -> (document title, meta description). Keep in lockstep with PAGES.
SEO_FOR_URL = {
    "": (
        "COREXION | We Raise Standards",
        "COREXION brings project leadership, engineering insight and design intelligence together for ambitious places worldwide.",
    ),
    "contact": (
        "Contact | COREXION",
        "Start a conversation with COREXION. Reach our offices and discuss project leadership, engineering and design support.",
    ),
    "insights": (
        "Insights | COREXION",
        "Perspectives from COREXION on projects, engineering, design and delivering long-term value across complex programmes.",
    ),
    "sectors": (
        "Sectors | COREXION",
        "COREXION works across sectors where integrated project leadership, engineering and design make a measurable difference.",
    ),
    "about/leadership": (
        "Leadership & Experts | COREXION",
        "Meet the COREXION leadership and specialists who guide projects with commercial, technical and design expertise.",
    ),
    "about/our-approach": (
        "Our Approach | COREXION",
        "How COREXION discovers, defines, designs, delivers and enhances projects through an integrated delivery approach.",
    ),
    "about/global-presence": (
        "Global Presence | COREXION",
        "COREXION combines a global perspective with local understanding across our international network of offices.",
    ),
    "about/vision-mission": (
        "Vision, Mission & Values | COREXION",
        "The vision, mission and values that shape how COREXION leads projects, engineering and design.",
    ),
    "expertise": (
        "Expertise | COREXION",
        "Explore COREXION expertise across project management, consulting engineering, design and commercial services.",
    ),
    "expertise/project-management": (
        "Project Management | COREXION",
        "Programme leadership, project controls, risk, commercial management and delivery assurance from COREXION.",
    ),
    "expertise/consulting-engineering": (
        "Consulting Engineering | COREXION",
        "Consulting engineering from COREXION: design review, coordination, supervision, quality and commissioning support.",
    ),
    "expertise/design": (
        "Design | COREXION",
        "Architecture, interiors, masterplanning and design management that connect vision to delivery with COREXION.",
    ),
    "expertise/cost-management": (
        "Cost Management | COREXION",
        "Planning, estimating, budget control, cash flow and change management to keep project costs under control.",
    ),
    "expertise/cost-management-2": (
        "Cost Control | COREXION",
        "Informed cost decisions throughout the project lifecycle, from early estimates through delivery and closeout.",
    ),
    "expertise/post-contract": (
        "Post-Contract Services | COREXION",
        "Post-contract control after award: change, payment assessment, claims management and project closeout.",
    ),
    "expertise/tender-management": (
        "Tender Management | COREXION",
        "Procurement strategy, prequalification, tender documentation, bid evaluation, negotiation and award support.",
    ),
    "expertise/value-engineering": (
        "Value Engineering | COREXION",
        "Value engineering that improves outcomes without compromising quality, performance or long-term intent.",
    ),
    "expertise/schedule-management": (
        "Schedule Management | COREXION",
        "Baseline planning, progress monitoring, critical path analysis, recovery planning and delay analysis.",
    ),
    "expertise/construction-project": (
        "Construction Project Management | COREXION",
        "On-site construction leadership from COREXION to control programme, quality, cost and delivery outcomes.",
    ),
    "expertise/contracts-arbitration": (
        "Contracts & Arbitration | COREXION",
        "Contract management, entitlement analysis and structured dispute strategies aligned with the contract.",
    ),
}

if SEO_FOR_URL.keys() != PAGES.keys():
    missing = PAGES.keys() - SEO_FOR_URL.keys()
    extra = SEO_FOR_URL.keys() - PAGES.keys()
    raise RuntimeError(f"SEO_FOR_URL must match PAGES (missing={missing}, extra={extra})")


def canonical_url(url_key, site_url):
    base = site_url.rstrip("/")
    if not url_key:
        return base + "/"
    return f"{base}/{url_key}"


def seo_context(url_key, site_url):
    """Template context for titles, social tags, canonical URL and JSON-LD."""
    title, description = SEO_FOR_URL[url_key]
    site = site_url.rstrip("/")
    canonical = canonical_url(url_key, site)
    logo = site + LOGO_PATH
    home = site + "/"
    structured = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "name": SITE_NAME,
                "url": home,
                "logo": logo,
            },
            {
                "@type": "WebPage",
                "name": title,
                "url": canonical,
                "description": description,
                "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": home},
            },
        ],
    }
    return {
        "seo_title": title,
        "seo_description": description,
        "canonical_url": canonical,
        "og_image": logo,
        "json_ld": json.dumps(structured, ensure_ascii=True),
        "site_name": SITE_NAME,
    }
