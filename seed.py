"""Seed BAM Studio — detailed content. Admin from env only."""
import os
from app import app, db
from models import (
    User, SiteSetting, ThemeSetting, NavigationItem, Project, ProjectCategory,
    Service, PricingPlan, TeamMember, Partnership, SocialLink, Solution,
    ProcessStep, FAQ, SiteStat, ValueItem, Testimonial, BlogCategory, BlogPost,
    JobPosition, JobApplication
)
from utils.helpers import DEFAULT_THEME
from slugify import slugify
from datetime import datetime


def seed():
    with app.app_context():
        db.create_all()

        email = (os.environ.get("ADMIN_EMAIL") or "admin@argonbhujel").strip().lower()
        password = os.environ.get("ADMIN_PASSWORD") or "Argon_017"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, name="Admin")
            user.set_password(password)
            db.session.add(user)
            print(f"Admin created: {email}")
        else:
            user.set_password(password)
            print(f"Admin password refreshed: {email}")

        # —— Site settings ——
        defaults = {
            "site_name": "BAM Studio",
            "tagline": "We design, build and maintain digital products for modern businesses.",
            "description": "BAM Studio is a digital development and creative technology studio building modern websites, custom software and digital experiences.",
            "email": "info@argan.com.np",
            "phone": "",
            "whatsapp": "",
            "address": "Nepal",
            "business_hours": "Sun–Fri · 10:00–18:00 NPT",
            "copyright_text": "© 2026 BAM Studio. Designed & Developed by BAM Studio.",
            "about_intro": "BAM Studio is a digital development and creative technology studio. We build modern websites, custom software and digital experiences that help businesses move forward.",
            "about_what_we_do": "We design, develop and maintain websites, e-commerce platforms, business systems, UI/UX and creative digital assets — with a focus on clarity, performance and long-term support.",
            "about_approach": "We start from real business needs, not templates. Discovery, clear planning, design, development, testing and ongoing support — so what we ship is usable and maintainable.",
            "mission": "To deliver digital products that are clear, reliable and built around how businesses actually work.",
            "vision": "To be a trusted technology partner for growing businesses in Nepal and beyond.",
            "hero_eyebrow": "BAM STUDIO",
            "hero_heading": "We Build Digital Experiences That Move Businesses Forward.",
            "hero_description": "Modern websites, custom software and digital experiences built around real business needs.",
            "hero_image": "",
            "hero_primary_text": "Start a Project",
            "hero_primary_url": "/quote",
            "hero_secondary_text": "View Our Work",
            "hero_secondary_url": "/work",
        }
        for k, v in defaults.items():
            s = SiteSetting.query.filter_by(key=k).first()
            if not s:
                db.session.add(SiteSetting(key=k, value=v))
            else:
                s.value = v

        for k, v in DEFAULT_THEME.items():
            existing = ThemeSetting.query.filter_by(key=k).first()
            if not existing:
                db.session.add(ThemeSetting(key=k, value=v))
            elif k.startswith("color_") or k == "theme_mode":
                existing.value = v

        # —— Navigation ——
        NavigationItem.query.delete()
        db.session.flush()
        top = [
            ("Home", "/", 0, False),
            ("Services", "/services", 1, False),
            ("Work", "/work", 2, False),
            ("Solutions", "/solutions", 3, False),
            ("Pricing", "/pricing", 4, False),
            ("About", "/about", 5, False),
        ]
        for label, url, order, cta in top:
            db.session.add(NavigationItem(label=label, url=url, order=order, is_cta=cta, is_visible=True))
        db.session.flush()
        more = NavigationItem(label="More", url="#", order=6, is_cta=False, is_visible=True)
        db.session.add(more)
        db.session.flush()
        for i, (label, url) in enumerate([
            ("Our Team", "/team"),
            ("Process", "/process"),
            ("Testimonials", "/testimonials"),
            ("FAQ", "/faq"),
            ("Insights", "/blog"),
            ("Careers", "/careers"),
        ]):
            db.session.add(NavigationItem(label=label, url=url, order=i, parent_id=more.id, is_visible=True))
        db.session.add(NavigationItem(label="Get a Quote", url="/quote", order=7, is_cta=True, is_visible=True))

        # —— Services (detailed) ——
        Service.query.delete()
        services = [
            {
                "title": "Web Development",
                "icon": "🌐",
                "description": "Modern, responsive websites built for performance, clarity and growth.",
                "full_description": "We design and develop custom websites from the ground up — marketing sites, company profiles, landing pages and content-driven platforms. Clean code, fast load times, mobile-first layout and structure that is easy to maintain.",
                "features": ["Responsive design", "Custom CMS-ready structure", "SEO-friendly markup", "Performance focused", "Contact & lead forms", "Ongoing support options"],
                "technologies": ["HTML5", "CSS3", "JavaScript", "Flask", "PostgreSQL"],
                "deliverables": ["Fully responsive website", "Admin-ready content structure where needed", "Basic SEO setup", "Deployment support"],
                "timeline": "2–6 weeks",
                "starting_price": "4,999",
            },
            {
                "title": "UI/UX Design",
                "icon": "✨",
                "description": "Interfaces and experiences focused on usability and brand clarity.",
                "full_description": "We design user interfaces and flows that feel clear and intentional. From wireframes to high-fidelity UI, we align design with how users actually move through your product.",
                "features": ["Wireframes & flows", "High-fidelity UI", "Design system basics", "Mobile & desktop", "Handoff-ready assets"],
                "technologies": ["Figma", "Design systems"],
                "deliverables": ["UI designs", "Key user flows", "Asset export / handoff"],
                "timeline": "1–4 weeks",
                "starting_price": "9,999",
            },
            {
                "title": "Custom Software",
                "icon": "⚙️",
                "description": "Software tailored to your workflows — not off-the-shelf compromises.",
                "full_description": "Internal tools, business systems and custom applications built around your processes. We focus on reliability, clear UX and maintainable architecture.",
                "features": ["Requirements workshop", "Custom workflows", "Role-based access", "Integrations", "Documentation & handover"],
                "technologies": ["Python", "Flask", "PostgreSQL", "REST APIs"],
                "deliverables": ["Working application", "Admin/user access", "Basic documentation"],
                "timeline": "4–12+ weeks",
                "starting_price": "24,999",
            },
            {
                "title": "E-commerce",
                "icon": "🛒",
                "description": "Online stores that are clear to browse and ready to sell.",
                "full_description": "Product catalogues, cart and checkout flows, order handling and storefront design built for real sales — not just a template with a payment button.",
                "features": ["Product catalogue", "Cart & checkout", "Order management basics", "Mobile-friendly storefront", "Payment integration options"],
                "technologies": ["Flask", "PostgreSQL", "Payment gateways"],
                "deliverables": ["Live storefront", "Admin product management", "Order flow"],
                "timeline": "4–10 weeks",
                "starting_price": "19,999",
            },
            {
                "title": "Business Automation",
                "icon": "📊",
                "description": "Automate repetitive work so your team can focus on what matters.",
                "full_description": "Forms, notifications, simple workflows and integrations that reduce manual copy-paste and follow-ups across your operations.",
                "features": ["Process mapping", "Automated notifications", "Form → system flows", "Simple dashboards"],
                "technologies": ["Python", "APIs", "Webhooks"],
                "deliverables": ["Automated workflows", "Admin visibility", "Handover notes"],
                "timeline": "2–8 weeks",
                "starting_price": "14,999",
            },
            {
                "title": "Maintenance & Support",
                "icon": "🔧",
                "description": "Keep your site and systems stable, updated and secure.",
                "full_description": "Ongoing care for websites and applications: updates, backups, small changes, monitoring and priority fixes when something breaks.",
                "features": ["Updates & patches", "Backups", "Small content/feature changes", "Priority support window"],
                "technologies": ["Depends on your stack"],
                "deliverables": ["Monthly care plan", "Change log", "Support channel"],
                "timeline": "Ongoing",
                "starting_price": "2,999",
            },
            {
                "title": "AI & Automation",
                "icon": "🤖",
                "description": "Practical AI assistants and automation where they actually help.",
                "full_description": "Chat assistants, content helpers and process automation using modern AI APIs — scoped to real use cases, not hype.",
                "features": ["Use-case scoping", "API integration", "Prompt & flow design", "Admin controls where needed"],
                "technologies": ["Python", "AI APIs", "Flask"],
                "deliverables": ["Working AI feature", "Basic admin/config", "Usage notes"],
                "timeline": "2–8 weeks",
                "starting_price": "19,999",
            },
            {
                "title": "Video Editing",
                "icon": "🎬",
                "description": "Clean cuts, captions and brand-ready video for web and social.",
                "full_description": "Short-form and mid-length video editing for marketing, product and social — consistent with your brand and platform requirements.",
                "features": ["Cut & colour", "Captions / subtitles", "Basic motion", "Export for web & social"],
                "technologies": ["Professional editors"],
                "deliverables": ["Final exports", "Source project on request"],
                "timeline": "3–10 days per piece",
                "starting_price": "2,999",
            },
            {
                "title": "Graphics Designing",
                "icon": "🎨",
                "description": "Visual identity assets that stay consistent across channels.",
                "full_description": "Logos, social creatives, banners and basic brand kits so your digital presence looks intentional and consistent.",
                "features": ["Logo / mark options", "Social templates", "Banners & covers", "Simple brand kit"],
                "technologies": ["Figma", "Illustrator-compatible export"],
                "deliverables": ["Source files", "Export pack (PNG/SVG)"],
                "timeline": "3–14 days",
                "starting_price": "3,999",
            },
        ]
        for i, s in enumerate(services):
            db.session.add(Service(
                title=s["title"], slug=slugify(s["title"]), description=s["description"],
                full_description=s["full_description"], icon=s["icon"],
                features=s["features"], technologies=s["technologies"],
                deliverables=s["deliverables"], timeline=s["timeline"],
                starting_price=s["starting_price"], currency="NPR",
                order=i, is_visible=True, cta_text="Get a Quote", cta_url="/quote"
            ))

        # —— Categories & Projects ——
        cats = {}
        for name in ["Sports / Football Club", "Portfolio / Developer Website", "Education", "Hospitality"]:
            c = ProjectCategory.query.filter_by(name=name).first()
            if not c:
                c = ProjectCategory(name=name, slug=slugify(name))
                db.session.add(c)
                db.session.flush()
            cats[name] = c

        projects_data = [
            ("Jhapa City FC", "Sports / Football Club", "https://jhapacityfc.vercel.app",
             "Official digital presence for Jhapa City FC — match centre, news and fan experience.",
             "Football club needed a modern digital home with fixtures, news and brand presence.",
             "Custom club website with match-focused UX, content structure and tech partnership support.",
             "2024–2026", "Sports"),
            ("Argan", "Portfolio / Developer Website", "https://argan.com.np",
             "Personal portfolio and developer website.",
             "Need for a clear personal brand and project showcase.",
             "Clean portfolio site with project highlights and contact path.",
             "2024", "Portfolio"),
            ("New Vision Academy", "Education", "https://newvisionacademy.com.np",
             "Education institution website.",
             "School needed an online presence for information and trust.",
             "Informative education website with clear structure and contact.",
             "2024", "Education"),
            ("Hotel Grand Garden", "Hospitality", "https://hotelgrand.com.np",
             "Hospitality website for Hotel Grand Garden.",
             "Hotel required a modern site for rooms, amenities and enquiries.",
             "Hospitality-focused website with enquiry flow.",
             "2024", "Hospitality"),
            ("Morang Model Residential", "Education", "https://morangmodelresidental.vercel.app",
             "Residential school website.",
             "Residential school needed a clear online profile.",
             "Education site with programme and contact information.",
             "2025", "Education"),
            ("Moonlight Model", "Education", "https://moonlightmodel.vercel.app",
             "Education website for Moonlight Model.",
             "Institution needed a simple, professional web presence.",
             "Clean education website with key sections and contact.",
             "2025", "Education"),
        ]
        for i, (name, cat_name, url, desc, challenge, solution, year, industry) in enumerate(projects_data):
            existing = Project.query.filter_by(slug=slugify(name)).first()
            if not existing:
                db.session.add(Project(
                    name=name, slug=slugify(name), category_id=cats[cat_name].id,
                    short_description=desc, challenge=challenge, solution=solution,
                    live_url=url, year=year, industry=industry,
                    is_featured=True, is_published=True, order=i,
                    technologies=["HTML", "CSS", "JavaScript", "Flask"] if "Jhapa" in name else ["HTML", "CSS", "JavaScript"],
                    services_used=["Web Development"],
                    features=["Responsive design", "Content sections", "Contact / enquiry"],
                ))
            else:
                existing.challenge = challenge
                existing.solution = solution
                existing.year = year
                existing.industry = industry

        # —— Solutions (industry) ——
        Solution.query.delete()
        solutions = [
            ("Education Websites", "Education", "🏫",
             "Schools and academies need clear information and trust online.",
             "Parents and students struggle to find reliable programme, admission and contact info.",
             "Structured education websites with programmes, about, gallery and enquiry forms.",
             ["Programme pages", "Admission / contact forms", "Mobile-friendly layout", "Easy content updates"]),
            ("Hospitality & Hotels", "Hospitality", "🏨",
             "Hotels need a site that showcases rooms and converts enquiries.",
             "Outdated or unclear sites lose bookings and credibility.",
             "Hospitality sites with rooms, amenities, gallery and enquiry/booking path.",
             ["Room showcase", "Enquiry forms", "Gallery", "Map & contact"]),
            ("Sports Clubs", "Sports", "⚽",
             "Clubs need match info, news and brand presence in one place.",
             "Fans and partners lack a single official digital home.",
             "Club platforms with fixtures, news, squad and partner visibility.",
             ["Match centre style sections", "News", "Squad / team", "Partner logos"]),
            ("Business Profiles", "Business", "💼",
             "SMEs need a professional digital face without complexity.",
             "No site or a weak one makes the business look smaller than it is.",
             "Clean company websites with services, about, work and contact.",
             ["Services", "About", "Contact", "Optional portfolio"]),
        ]
        for i, (title, industry, icon, short, problem, sol, features) in enumerate(solutions):
            db.session.add(Solution(
                title=title, slug=slugify(title), industry=industry, icon=icon,
                short_description=short, problem=problem, solution_text=sol,
                features=features, technologies=["HTML", "CSS", "JavaScript", "Flask"],
                order=i, is_visible=True, cta_url="/quote"
            ))

        # —— Process ——
        ProcessStep.query.delete()
        steps = [
            (1, "Discovery", "We learn your goals, audience, constraints and success criteria.",
             "Business goals, examples of sites you like, content/assets you already have.",
             "A clear brief and recommended scope."),
            (2, "Planning", "We define structure, pages, features and timeline.",
             "Feedback on proposed sitemap and priorities.",
             "Agreed plan, timeline and milestones."),
            (3, "UI/UX Design", "Layouts and visual design for key screens.",
             "Brand preferences, logo/assets, feedback on drafts.",
             "Approved design direction for development."),
            (4, "Development", "We build the front end, integrations and any CMS/admin.",
             "Content (text, images), access for third-party tools if needed.",
             "Working product in staging for review."),
            (5, "Testing", "Cross-device checks, forms, links and basic performance.",
             "Feedback list from your review.",
             "Fixes applied and sign-off ready build."),
            (6, "Deployment", "Go-live on your domain/hosting with final checks.",
             "Domain/DNS access or preferred host details.",
             "Live site and handover notes."),
            (7, "Support", "Optional care: updates, small changes and priority fixes.",
             "Requests via agreed channel.",
             "Stable site and ongoing improvements as agreed."),
        ]
        for num, title, happens, client, delivers in steps:
            db.session.add(ProcessStep(
                step_number=num, title=title, what_happens=happens,
                client_provides=client, bam_delivers=delivers,
                order=num, is_visible=True
            ))

        # —— FAQ ——
        FAQ.query.delete()
        faqs = [
            ("How much does a website cost?",
             "Starting packages begin from NPR 4,999+ depending on scope. A simple brochure site is at the lower end; e-commerce, custom software or multi-language sites cost more. We quote after understanding your requirements."),
            ("How long does development take?",
             "Typical marketing websites take about 2–6 weeks. Larger projects (e-commerce, custom systems) can take 1–3 months or more. Timeline is agreed during planning."),
            ("Do you provide hosting?",
             "We can advise on hosting and deploy for you. Hosting can be on your preferred provider (e.g. Vercel, shared hosting, VPS) or we can recommend options."),
            ("Can I update my website myself?",
             "Yes, when we set up a CMS or structured admin. For purely static sites, content changes can be handled by us under a maintenance plan."),
            ("Do you provide maintenance?",
             "Yes. Maintenance & Support covers updates, backups, small changes and priority fixes on an agreed plan."),
            ("Can you build custom software?",
             "Yes. We build internal tools, business systems and custom web applications around your workflows."),
            ("Do you work with clients outside Nepal?",
             "Yes. We work remotely with clear communication and can support clients outside Nepal."),
            ("What technologies do you use?",
             "Primarily HTML, CSS, JavaScript, Python/Flask, PostgreSQL, and modern deployment platforms. Stack is chosen to fit the project — not forced."),
            ("How do I start a project?",
             "Send a message via Get a Quote or Contact with your goals and constraints. We reply with questions or a proposed next step — often a short discovery call."),
            ("Do you provide domain and hosting?",
             "We can guide domain purchase and DNS, and handle deployment. Domain registration is usually under your ownership; we help with setup."),
        ]
        for i, (q, a) in enumerate(faqs):
            db.session.add(FAQ(question=q, answer=a, order=i, is_visible=True))

        extra_faqs = [
            ("Do you provide source code?", "Source code ownership is agreed per project. For most custom builds, you receive the deliverables and access needed to run and maintain the product."),
            ("How many revisions are included?", "Revision rounds are defined in the proposal/scope. Standard packages include a reasonable set of revision rounds; more can be added."),
            ("Can you redesign my existing website?", "Yes. We can redesign and rebuild existing sites with improved structure, performance and content."),
            ("Do you provide SEO?", "We implement SEO-friendly structure, meta basics and clean markup. Advanced SEO campaigns can be scoped separately."),
            ("Do you integrate payment gateways?", "Yes, where the project requires it — subject to gateway availability and compliance for your market."),
            ("Can you migrate an existing website?", "Yes. Content and site migration can be part of the project scope."),
            ("Do you provide admin panels?", "Yes. CMS/admin panels are available when the project needs editable content."),
            ("Do you provide technical support after launch?", "Yes. Maintenance & Support plans cover updates, fixes and small changes after launch."),
            ("Do you offer remote work?", "Yes. Roles may be remote, on-site or hybrid depending on the position."),
            ("Do you hire interns?", "Yes. Internship and trainee openings are listed on the Careers page when available."),
            ("Can freshers apply?", "Yes, when the role allows 0–2 years experience. Check each job posting."),
            ("Do you hire freelancers?", "Yes. Freelance/contract roles and our freelancer network are listed under Careers."),
            ("What technologies do you use?", "Primarily HTML, CSS, JavaScript, Python/Flask, PostgreSQL and modern hosting. Stack is chosen per project."),
            ("How can I apply?", "Open a position on Careers and use Apply, or send a general application."),
            ("Can I send a general application?", "Yes — use Send Your Resume / General Application on the Careers page."),
            ("How long does the hiring process take?", "It varies by role. We aim to review applications and respond when there is a match."),
        ]
        existing_q = {f.question for f in FAQ.query.all()}
        base_order = FAQ.query.count()
        for i, (q, a) in enumerate(extra_faqs):
            if q not in existing_q:
                db.session.add(FAQ(question=q, answer=a, order=base_order + i, is_visible=True))


        # —— Stats & Values ——
        SiteStat.query.delete()
        for i, (val, label) in enumerate([
            ("20+", "Projects"), ("15+", "Clients"), ("10+", "Technologies"), ("24/7", "Support"),
        ]):
            db.session.add(SiteStat(value=val, label=label, order=i, is_visible=True))

        ValueItem.query.delete()
        for i, (title, desc) in enumerate([
            ("Quality", "We ship work we are willing to put our name on."),
            ("Innovation", "We use modern tools where they improve the outcome — not for show."),
            ("Transparency", "Clear scope, timelines and communication."),
            ("Reliability", "Stable delivery and support after launch."),
            ("Client-first", "Decisions start from your business goals."),
        ]):
            db.session.add(ValueItem(title=title, description=desc, order=i, is_visible=True))

        # —— Pricing ——
        if PricingPlan.query.count() == 0:
            plans = [
                ("Basic", "4,999", "Starter websites and simple presence.",
                 ["Responsive design", "Core pages", "Contact form", "Basic SEO"], False, None, 0),
                ("Standard", "9,999", "Professional business websites.",
                 ["Custom design", "CMS-ready structure", "SEO basics", "Support window"], True, "Popular", 1),
                ("Premium", "24,999", "Advanced sites with richer features.",
                 ["Custom UI", "Integrations", "Performance focus", "Ongoing support option"], False, None, 2),
                ("Custom", "39,999", "Fully custom software and digital systems.",
                 ["Discovery workshop", "Custom development", "Dedicated support"], False, None, 3),
            ]
            for name, price, desc, features, feat, badge, order in plans:
                db.session.add(PricingPlan(
                    name=name, price=price, currency="NPR", description=desc,
                    features=features, is_featured=feat, badge=badge, order=order,
                    is_visible=True, button_url="/quote"
                ))

        # —— Team ——
        if TeamMember.query.count() == 0:
            team = [
                ("Argon Bhujel", "Founder / Full-Stack Developer",
                 "Leads product, architecture and full-stack delivery at BAM Studio.",
                 ["Python", "Flask", "JavaScript", "PostgreSQL", "UI systems"], 0),
                ("Manzil Bhujel", "Frontend Developer",
                 "Focuses on responsive interfaces, interaction and front-end quality.",
                 ["HTML", "CSS", "JavaScript", "Responsive UI"], 1),
                ("Bashu Chhetri", "Marketing & Finance",
                 "Supports growth, client communication and operations.",
                 ["Marketing", "Client relations", "Operations"], 2),
            ]
            for name, pos, bio, skills, order in team:
                db.session.add(TeamMember(
                    name=name, position=pos, bio=bio, skills=skills,
                    order=order, is_visible=True
                ))

        # —— Partnership ——
        if Partnership.query.count() == 0:
            db.session.add(Partnership(
                partner_name="Jhapa FC",
                badge_text="Official Web & Tech Partner of Jhapa FC",
                description="BAM Studio works on digital and technology solutions for Jhapa FC.",
                partner_url="https://jhapacityfc.vercel.app",
                is_featured=True, is_visible=True, order=0,
            ))

        # —— Testimonials: empty by default (no fake reviews) ——
        # Leave empty — section hides when none

        for platform, url in [
            ("Facebook", ""), ("Instagram", ""), ("LinkedIn", ""), ("GitHub", ""), ("YouTube", "")
        ]:
            if not SocialLink.query.filter_by(platform=platform).first():
                db.session.add(SocialLink(platform=platform, url=url, is_visible=bool(url)))

        
        # Job positions sample
        if JobPosition.query.count() == 0:
            sample_jobs = [
                ("Frontend Developer", "Full-time", "Remote / On-site", "0–2 Years", False, False,
                 ["Build responsive interfaces", "Collaborate with designers", "Maintain UI quality"],
                 ["HTML, CSS, JavaScript", "Problem-solving", "Git basics"]),
                ("Full-Stack Developer", "Full-time", "Remote / On-site", "1–3 Years", False, False,
                 ["Build web applications", "Develop APIs", "Work with databases", "Deploy applications"],
                 ["Python/JavaScript", "Git/GitHub", "Communication"]),
                ("UI/UX Designer", "Full-time", "Remote", "0–2 Years", False, False,
                 ["Design user flows and UI", "Create consistent visuals", "Handoff to developers"],
                 ["Figma or similar", "Portfolio", "Attention to detail"]),
                ("Web Development Intern", "Internship", "Remote / Hybrid", "Fresher", True, False,
                 ["Assist on real client projects", "Learn modern web stack", "Ship under guidance"],
                 ["Willingness to learn", "Basic HTML/CSS interest"]),
                ("Freelance Developer", "Freelance", "Remote", "Flexible", False, True,
                 ["Project-based development", "Clear delivery milestones"],
                 ["Proven skills", "Reliable communication"]),
            ]
            for i, (title, emp, mode, exp, intern, free, resp, req) in enumerate(sample_jobs):
                db.session.add(JobPosition(
                    title=title, slug=slugify(title), employment_type=emp, work_mode=mode,
                    location="Nepal", experience=exp, is_internship=intern, is_freelance=free,
                    about_role=f"Join BAM Studio as {title}.",
                    responsibilities=resp, requirements=req,
                    what_we_offer=["Flexible environment", "Real projects", "Learning opportunities"],
                    is_published=True, order=i,
                ))

        db.session.commit()
        print("Seed completed.")
        print(f"Login → {email} / (password from ADMIN_PASSWORD or Argon_017)")


if __name__ == "__main__":
    seed()
