import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, Response, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect, CSRFError
from config import Config
from models import (
    db, User, Project, ProjectCategory, ProjectImage, Service, PricingPlan,
    TeamMember, Partnership, Testimonial, BlogPost, BlogCategory, Lead,
    NavigationItem, HomepageSection, Media, SocialLink, SEOSetting,
    Solution, ProcessStep, FAQ, SiteStat, ValueItem, JobPosition, JobApplication
)
from utils.helpers import get_setting, get_theme, get_all_theme, get_all_settings, generate_css_variables, set_setting, set_theme, DEFAULT_THEME
from datetime import datetime
from slugify import slugify
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf = CSRFProtect(app)

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash("Session expired or invalid form. Please try again.", "error")
    # Prefer referring page or admin dashboard
    ref = request.referrer
    if ref and request.host in ref:
        return redirect(ref)
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("admin_login"))


login_manager = LoginManager(app)
login_manager.login_view = "admin_login"
login_manager.login_message_category = "warning"

if app.config["CLOUDINARY_CLOUD_NAME"]:
    cloudinary.config(
        cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=app.config["CLOUDINARY_API_KEY"],
        api_secret=app.config["CLOUDINARY_API_SECRET"],
        secure=True,
    )


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.context_processor
def inject_globals():
    settings = get_all_settings()
    theme = get_all_theme()
    all_nav = NavigationItem.query.filter_by(is_visible=True).order_by(NavigationItem.order).all()
    top_nav = [n for n in all_nav if n.parent_id is None]
    children_map = {}
    for n in all_nav:
        if n.parent_id is not None:
            children_map.setdefault(n.parent_id, []).append(n)
    socials = SocialLink.query.filter(SocialLink.url.isnot(None), SocialLink.url != "", SocialLink.is_visible == True).order_by(SocialLink.order).all()
    partnership = Partnership.query.filter_by(is_featured=True, is_visible=True).first()
    return {
        "site": settings,
        "theme": theme,
        "nav_items": top_nav,
        "nav_children": children_map,
        "social_links": socials,
        "featured_partnership": partnership,
        "css_vars": generate_css_variables(theme),
        "now": datetime.utcnow(),
    }


# ---------- PUBLIC ROUTES ----------

@app.route("/")
def index():
    sections = HomepageSection.query.filter_by(is_visible=True).order_by(HomepageSection.order).all()
    projects = Project.query.filter_by(is_published=True, is_featured=True).order_by(Project.order, Project.id.desc()).limit(6).all()
    services = Service.query.filter_by(is_visible=True).order_by(Service.order).limit(6).all()
    pricing = PricingPlan.query.filter_by(is_visible=True).order_by(PricingPlan.order).all()
    team = TeamMember.query.filter_by(is_visible=True).order_by(TeamMember.order).all()
    testimonials = Testimonial.query.filter_by(is_published=True).order_by(Testimonial.order).all()
    partnership = Partnership.query.filter_by(is_visible=True).order_by(Partnership.order).all()
    stats = SiteStat.query.filter_by(is_visible=True).order_by(SiteStat.order).all()
    process_steps = ProcessStep.query.filter_by(is_visible=True).order_by(ProcessStep.order).limit(4).all()
    return render_template(
        "public/index.html",
        sections=sections,
        projects=projects,
        services=services,
        pricing=pricing,
        team=team,
        testimonials=testimonials,
        partnerships=partnership,
        stats=stats,
        process_steps=process_steps,
    )


@app.route("/services")
def services_page():
    services = Service.query.filter_by(is_visible=True).order_by(Service.order).all()
    return render_template("public/services.html", services=services)


@app.route("/services/<slug>")
def service_detail(slug):
    service = Service.query.filter_by(slug=slug, is_visible=True).first_or_404()
    return render_template("public/service_detail.html", service=service)


@app.route("/work")
def work_page():
    projects = Project.query.filter_by(is_published=True).order_by(Project.order, Project.id.desc()).all()
    categories = ProjectCategory.query.all()
    return render_template("public/work.html", projects=projects, categories=categories)


@app.route("/work/<slug>")
def project_detail(slug):
    project = Project.query.filter_by(slug=slug, is_published=True).first_or_404()
    related = Project.query.filter(Project.id != project.id, Project.is_published == True).order_by(Project.order).limit(3).all()
    return render_template("public/project_detail.html", project=project, related=related)


@app.route("/pricing")
def pricing_page():
    plans = PricingPlan.query.filter_by(is_visible=True).order_by(PricingPlan.order).all()
    return render_template("public/pricing.html", plans=plans)


@app.route("/about")
def about_page():
    team = TeamMember.query.filter_by(is_visible=True).order_by(TeamMember.order).all()
    partnerships = Partnership.query.filter_by(is_visible=True).order_by(Partnership.order).all()
    stats = SiteStat.query.filter_by(is_visible=True).order_by(SiteStat.order).all()
    values = ValueItem.query.filter_by(is_visible=True).order_by(ValueItem.order).all()
    return render_template("public/about.html", team=team, partnerships=partnerships, stats=stats, values=values)


@app.route("/contact", methods=["GET", "POST"])
def contact_page():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            if not name or not email:
                flash("Name and email are required.", "error")
                return redirect(url_for("contact_page"))
            lead = Lead(
                name=name,
                email=email,
                phone=request.form.get("phone", "").strip(),
                company=request.form.get("company", "").strip(),
                service=request.form.get("service", "").strip(),
                budget=request.form.get("budget", "").strip(),
                message=request.form.get("message", "").strip(),
                status="NEW",
            )
            db.session.add(lead)
            db.session.commit()
            flash("Thank you! We will get back to you soon.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Could not send message. Please try again. ({e})", "error")
        return redirect(url_for("contact_page"))
    services = Service.query.filter_by(is_visible=True).order_by(Service.order).all()
    return render_template("public/contact.html", services=services)


@app.route("/blog")
def blog_page():
    posts = BlogPost.query.filter_by(status="published").order_by(BlogPost.published_at.desc()).all()
    return render_template("public/blog.html", posts=posts)


@app.route("/blog/<slug>")
def blog_detail(slug):
    post = BlogPost.query.filter_by(slug=slug, status="published").first_or_404()
    return render_template("public/blog_detail.html", post=post)


@app.route("/robots.txt")
def robots():
    return Response("User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    pages = [
        url_for("index", _external=True),
        url_for("services_page", _external=True),
        url_for("work_page", _external=True),
        url_for("solutions_page", _external=True),
        url_for("pricing_page", _external=True),
        url_for("about_page", _external=True),
        url_for("team_page", _external=True),
        url_for("process_page", _external=True),
        url_for("faq_page", _external=True),
        url_for("testimonials_page", _external=True),
        url_for("quote_page", _external=True),
        url_for("contact_page", _external=True),
        url_for("blog_page", _external=True),
        url_for("careers_page", _external=True),
    ]
    for p in Project.query.filter_by(is_published=True).all():
        pages.append(url_for("project_detail", slug=p.slug, _external=True))
    for s in Service.query.filter_by(is_visible=True).all():
        pages.append(url_for("service_detail", slug=s.slug, _external=True))
    for b in BlogPost.query.filter_by(status="published").all():
        pages.append(url_for("blog_detail", slug=b.slug, _external=True))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in pages:
        xml.append(f"<url><loc>{u}</loc></url>")
    xml.append("</urlset>")
    return Response("\n".join(xml), mimetype="application/xml")


@app.errorhandler(404)
def not_found(e):
    try:
        return render_template("public/404.html"), 404
    except Exception:
        return "<h1>404</h1><p>Page not found.</p><a href='/'>Home</a>", 404


@app.errorhandler(403)
def forbidden(e):
    return render_template("public/403.html"), 403


@app.errorhandler(500)
def server_error(e):
    try:
        return render_template("public/500.html"), 500
    except Exception:
        return "<h1>500</h1><p>Server error.</p>", 500



@app.route("/solutions")
def solutions_page():
    solutions = Solution.query.filter_by(is_visible=True).order_by(Solution.order).all()
    return render_template("public/solutions.html", solutions=solutions)


@app.route("/solutions/<slug>")
def solution_detail(slug):
    solution = Solution.query.filter_by(slug=slug, is_visible=True).first_or_404()
    return render_template("public/solution_detail.html", solution=solution)


@app.route("/team")
def team_page():
    team = TeamMember.query.filter_by(is_visible=True).order_by(TeamMember.order).all()
    return render_template("public/team.html", team=team)


@app.route("/team/<int:mid>")
def team_detail(mid):
    member = TeamMember.query.filter_by(id=mid, is_visible=True).first_or_404()
    return render_template("public/team_detail.html", member=member)


@app.route("/process")
def process_page():
    steps = ProcessStep.query.filter_by(is_visible=True).order_by(ProcessStep.order).all()
    return render_template("public/process.html", steps=steps)


@app.route("/faq")
def faq_page():
    faqs = FAQ.query.filter_by(is_visible=True).order_by(FAQ.order).all()
    return render_template("public/faq.html", faqs=faqs)


@app.route("/testimonials")
def testimonials_page():
    testimonials = Testimonial.query.filter_by(is_published=True).order_by(Testimonial.order).all()
    return render_template("public/testimonials.html", testimonials=testimonials)


@app.route("/quote", methods=["GET", "POST"])
def quote_page():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            if not name or not email:
                flash("Name and email are required.", "error")
                return redirect(url_for("quote_page"))
            details = request.form.get("details", "").strip()
            extra = []
            if request.form.get("timeline"):
                extra.append(f"Timeline: {request.form.get('timeline')}")
            if request.form.get("reference"):
                extra.append(f"Reference: {request.form.get('reference')}")
            if extra:
                details = (details + "\n\n" + "\n".join(extra)).strip()
            lead = Lead(
                name=name,
                email=email,
                phone=request.form.get("phone", "").strip(),
                company=request.form.get("company", "").strip(),
                service=request.form.get("project_type", "").strip(),
                budget=request.form.get("budget", "").strip(),
                message=details,
                status="NEW",
            )
            db.session.add(lead)
            db.session.commit()
            flash("Thank you! We'll get back to you shortly.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Could not submit quote. Please try again. ({e})", "error")
        return redirect(url_for("quote_page"))
    services = Service.query.filter_by(is_visible=True).order_by(Service.order).all()
    return render_template("public/quote.html", services=services)




@app.route("/careers")
def careers_page():
    jobs = JobPosition.query.filter_by(is_published=True, is_closed=False, is_internship=False, is_freelance=False).order_by(JobPosition.order).all()
    internships = JobPosition.query.filter_by(is_published=True, is_closed=False, is_internship=True).order_by(JobPosition.order).all()
    freelancers = JobPosition.query.filter_by(is_published=True, is_closed=False, is_freelance=True).order_by(JobPosition.order).all()
    return render_template("public/careers.html", jobs=jobs, internships=internships, freelancers=freelancers)


@app.route("/careers/general-apply", methods=["GET", "POST"])
def career_general_apply():
    if request.method == "POST":
        try:
            name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            if not name or not email:
                flash("Name and email are required.", "error")
                return redirect(url_for("career_general_apply"))
            resume_url = request.form.get("resume_url", "").strip()
            if "resume" in request.files:
                f = request.files["resume"]
                if f and f.filename:
                    if app.config.get("CLOUDINARY_CLOUD_NAME"):
                        result = cloudinary.uploader.upload(f, folder="bam-studio/resumes", resource_type="auto")
                        resume_url = result["secure_url"]
                    else:
                        import os
                        from werkzeug.utils import secure_filename
                        os.makedirs(os.path.join(app.root_path, "static", "uploads", "resumes"), exist_ok=True)
                        fname = secure_filename(f.filename)
                        path = os.path.join(app.root_path, "static", "uploads", "resumes", fname)
                        f.save(path)
                        resume_url = url_for("static", filename=f"uploads/resumes/{fname}")
            application = JobApplication(
                full_name=name,
                email=email,
                phone=request.form.get("phone", "").strip(),
                position_title="General Application",
                experience=request.form.get("experience", "").strip(),
                portfolio=request.form.get("portfolio", "").strip(),
                github=request.form.get("github", "").strip(),
                linkedin=request.form.get("linkedin", "").strip(),
                cover_letter=request.form.get("message", "").strip(),
                resume_url=resume_url,
                expertise=request.form.get("expertise", "").strip(),
                message=request.form.get("message", "").strip(),
                application_type="general",
                status="NEW",
            )
            db.session.add(application)
            db.session.commit()
            flash("Application Submitted Successfully! Thank you for your interest in BAM Studio.", "success")
            return redirect(url_for("careers_page"))
        except Exception as e:
            db.session.rollback()
            flash(f"Could not submit. ({e})", "error")
            return redirect(url_for("career_general_apply"))
    return render_template("public/career_general_apply.html")

@app.route("/careers/<slug>")
def career_detail(slug):
    job = JobPosition.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template("public/career_detail.html", job=job)


@app.route("/careers/<slug>/apply", methods=["GET", "POST"])
def career_apply(slug):
    job = JobPosition.query.filter_by(slug=slug, is_published=True).first_or_404()
    if job.is_closed:
        flash("This position is closed.", "error")
        return redirect(url_for("career_detail", slug=slug))
    if request.method == "POST":
        try:
            name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            if not name or not email:
                flash("Name and email are required.", "error")
                return redirect(url_for("career_apply", slug=slug))
            resume_url = request.form.get("resume_url", "").strip()
            if "resume" in request.files:
                f = request.files["resume"]
                if f and f.filename:
                    if app.config.get("CLOUDINARY_CLOUD_NAME"):
                        result = cloudinary.uploader.upload(f, folder="bam-studio/resumes", resource_type="auto")
                        resume_url = result["secure_url"]
                    else:
                        import os
                        from werkzeug.utils import secure_filename
                        os.makedirs(os.path.join(app.root_path, "static", "uploads", "resumes"), exist_ok=True)
                        fname = secure_filename(f.filename)
                        path = os.path.join(app.root_path, "static", "uploads", "resumes", fname)
                        f.save(path)
                        resume_url = url_for("static", filename=f"uploads/resumes/{fname}")
            app_type = "internship" if job.is_internship else ("freelance" if job.is_freelance else "job")
            application = JobApplication(
                full_name=name,
                email=email,
                phone=request.form.get("phone", "").strip(),
                position_id=job.id,
                position_title=job.title,
                experience=request.form.get("experience", "").strip(),
                portfolio=request.form.get("portfolio", "").strip(),
                github=request.form.get("github", "").strip(),
                linkedin=request.form.get("linkedin", "").strip(),
                cover_letter=request.form.get("cover_letter", "").strip(),
                resume_url=resume_url,
                application_type=app_type,
                status="NEW",
            )
            db.session.add(application)
            db.session.commit()
            flash("Application Submitted Successfully! We'll review and contact you if there's a match.", "success")
            return redirect(url_for("career_detail", slug=slug))
        except Exception as e:
            db.session.rollback()
            flash(f"Could not submit application. ({e})", "error")
            return redirect(url_for("career_apply", slug=slug))
    return render_template("public/career_apply.html", job=job)




@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session.permanent = True
            login_user(user, remember=True, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for("admin_dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("admin/login.html")


@app.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for("admin_login"))


# ---------- ADMIN DASHBOARD ----------

@app.route("/admin")
@login_required
def admin_dashboard():
    stats = {
        "projects": Project.query.count(),
        "published_projects": Project.query.filter_by(is_published=True).count(),
        "leads": Lead.query.count(),
        "new_leads": Lead.query.filter_by(status="NEW").count(),
        "services": Service.query.count(),
        "blog": BlogPost.query.count(),
        "testimonials": Testimonial.query.count(),
        "team": TeamMember.query.count(),
        "media": Media.query.count(),
    }
    recent_leads = Lead.query.order_by(Lead.created_at.desc()).limit(5).all()
    recent_projects = Project.query.order_by(Project.updated_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, recent_leads=recent_leads, recent_projects=recent_projects)


# ---------- ADMIN: THEME ----------

@app.route("/admin/theme", methods=["GET", "POST"])
@login_required
def admin_theme():
    if request.method == "POST":
        for key in DEFAULT_THEME.keys():
            val = request.form.get(key)
            if val is not None:
                set_theme(key, val)
        flash("Theme updated successfully.", "success")
        return redirect(url_for("admin_theme"))
    theme = {**DEFAULT_THEME, **get_all_theme()}
    return render_template("admin/theme.html", theme=theme)


# ---------- ADMIN: PROJECTS ----------

@app.route("/admin/projects")
@login_required
def admin_projects():
    projects = Project.query.order_by(Project.order, Project.id.desc()).all()
    return render_template("admin/projects.html", projects=projects)


@app.route("/admin/projects/new", methods=["GET", "POST"])
@login_required
def admin_project_new():
    categories = ProjectCategory.query.all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        slug = request.form.get("slug") or slugify(name)
        p = Project(
            name=name,
            slug=slug,
            category_id=request.form.get("category_id") or None,
            client=request.form.get("client"),
            short_description=request.form.get("short_description"),
            full_description=request.form.get("full_description"),
            challenge=request.form.get("challenge"),
            solution=request.form.get("solution"),
            industry=request.form.get("industry"),
            year=request.form.get("year"),
            features=[f.strip() for f in request.form.get("features", "").split("\n") if f.strip()],
            technologies=[t.strip() for t in request.form.get("technologies", "").split(",") if t.strip()],
            services_used=[t.strip() for t in request.form.get("services_used", "").split(",") if t.strip()],
            results=request.form.get("results"),
            cover_image=request.form.get("cover_image"),
            live_url=request.form.get("live_url"),
            github_url=request.form.get("github_url"),
            project_date=request.form.get("project_date"),
            location=request.form.get("location"),
            is_featured=bool(request.form.get("is_featured")),
            is_published=bool(request.form.get("is_published")),
            order=int(request.form.get("order") or 0),
        )
        db.session.add(p)
        db.session.commit()
        flash("Project created.", "success")
        return redirect(url_for("admin_projects"))
    return render_template("admin/project_form.html", project=None, categories=categories)


@app.route("/admin/projects/<int:pid>/edit", methods=["GET", "POST"])
@login_required
def admin_project_edit(pid):
    project = Project.query.get_or_404(pid)
    categories = ProjectCategory.query.all()
    if request.method == "POST":
        project.name = request.form.get("name", "").strip()
        project.slug = request.form.get("slug") or slugify(project.name)
        project.category_id = request.form.get("category_id") or None
        project.client = request.form.get("client")
        project.industry = request.form.get("industry")
        project.year = request.form.get("year")
        project.short_description = request.form.get("short_description")
        project.full_description = request.form.get("full_description")
        project.challenge = request.form.get("challenge")
        project.solution = request.form.get("solution")
        project.results = request.form.get("results")
        project.features = [f.strip() for f in request.form.get("features", "").split("\n") if f.strip()]
        project.technologies = [t.strip() for t in request.form.get("technologies", "").split(",") if t.strip()]
        project.services_used = [t.strip() for t in request.form.get("services_used", "").split(",") if t.strip()]
        project.cover_image = request.form.get("cover_image")
        project.live_url = request.form.get("live_url")
        project.github_url = request.form.get("github_url")
        project.project_date = request.form.get("project_date")
        project.location = request.form.get("location")
        project.is_featured = bool(request.form.get("is_featured"))
        project.is_published = bool(request.form.get("is_published"))
        project.order = int(request.form.get("order") or 0)
        db.session.commit()
        flash("Project updated.", "success")
        return redirect(url_for("admin_projects"))
    return render_template("admin/project_form.html", project=project, categories=categories)


@app.route("/admin/projects/<int:pid>/delete", methods=["POST"])
@login_required
def admin_project_delete(pid):
    project = Project.query.get_or_404(pid)
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted.", "success")
    return redirect(url_for("admin_projects"))


# ---------- ADMIN: SERVICES ----------

@app.route("/admin/services")
@login_required
def admin_services():
    services = Service.query.order_by(Service.order).all()
    return render_template("admin/services.html", services=services)


@app.route("/admin/services/new", methods=["GET", "POST"])
@login_required
def admin_service_new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        s = Service(
            title=title,
            slug=request.form.get("slug") or slugify(title),
            description=request.form.get("description"),
            full_description=request.form.get("full_description"),
            icon=request.form.get("icon"),
            image=request.form.get("image"),
            features=[f.strip() for f in request.form.get("features", "").split("\n") if f.strip()],
            technologies=[t.strip() for t in request.form.get("technologies", "").split(",") if t.strip()],
            deliverables=[d.strip() for d in request.form.get("deliverables", "").split("\n") if d.strip()],
            timeline=request.form.get("timeline"),
            starting_price=request.form.get("starting_price"),
            currency=request.form.get("currency") or "NPR",
            cta_text=request.form.get("cta_text") or "Get a Quote",
            cta_url=request.form.get("cta_url") or "/quote",
            order=int(request.form.get("order") or 0),
            is_visible=bool(request.form.get("is_visible")),
        )
        db.session.add(s)
        db.session.commit()
        flash("Service created.", "success")
        return redirect(url_for("admin_services"))
    return render_template("admin/service_form.html", service=None)


@app.route("/admin/services/<int:sid>/edit", methods=["GET", "POST"])
@login_required
def admin_service_edit(sid):
    service = Service.query.get_or_404(sid)
    if request.method == "POST":
        service.title = request.form.get("title", "").strip()
        service.slug = request.form.get("slug") or slugify(service.title)
        service.description = request.form.get("description")
        service.full_description = request.form.get("full_description")
        service.icon = request.form.get("icon")
        service.image = request.form.get("image")
        service.features = [f.strip() for f in request.form.get("features", "").split("\n") if f.strip()]
        service.technologies = [t.strip() for t in request.form.get("technologies", "").split(",") if t.strip()]
        service.deliverables = [d.strip() for d in request.form.get("deliverables", "").split("\n") if d.strip()]
        service.timeline = request.form.get("timeline")
        service.starting_price = request.form.get("starting_price")
        service.currency = request.form.get("currency") or "NPR"
        service.cta_text = request.form.get("cta_text") or "Get a Quote"
        service.cta_url = request.form.get("cta_url") or "/quote"
        service.order = int(request.form.get("order") or 0)
        service.is_visible = bool(request.form.get("is_visible"))
        db.session.commit()
        flash("Service updated.", "success")
        return redirect(url_for("admin_services"))
    return render_template("admin/service_form.html", service=service)


# ---------- ADMIN: LEADS ----------

@app.route("/admin/leads")
@login_required
def admin_leads():
    status = request.args.get("status")
    q = Lead.query
    if status:
        q = q.filter_by(status=status)
    leads = q.order_by(Lead.created_at.desc()).all()
    return render_template("admin/leads.html", leads=leads, current_status=status)


@app.route("/admin/leads/<int:lid>", methods=["GET", "POST"])
@login_required
def admin_lead_detail(lid):
    lead = Lead.query.get_or_404(lid)
    if request.method == "POST":
        lead.status = request.form.get("status", lead.status)
        lead.notes = request.form.get("notes", lead.notes)
        db.session.commit()
        flash("Lead updated.", "success")
        return redirect(url_for("admin_lead_detail", lid=lid))
    return render_template("admin/lead_detail.html", lead=lead)


# ---------- ADMIN: GENERAL SETTINGS ----------

@app.route("/admin/settings", methods=["GET", "POST"])
@login_required
def admin_settings():
    keys = [
        "site_name", "tagline", "description", "logo", "dark_logo", "light_logo",
        "favicon", "email", "phone", "whatsapp", "address", "copyright_text",
        "google_maps_url", "business_hours",
        "about_intro", "about_what_we_do", "about_approach", "mission", "vision",
        "hero_eyebrow", "hero_heading", "hero_description", "hero_image", "hero_primary_text", "hero_primary_url", "hero_secondary_text", "hero_secondary_url",
        "custom_css", "custom_js", "header_scripts", "footer_scripts",
    ]
    if request.method == "POST":
        for k in keys:
            val = request.form.get(k)
            if val is not None:
                set_setting(k, val)
        flash("Settings saved.", "success")
        return redirect(url_for("admin_settings"))
    settings = get_all_settings()
    return render_template("admin/settings.html", settings=settings, keys=keys)


# ---------- ADMIN: NAVIGATION ----------

@app.route("/admin/navigation", methods=["GET", "POST"])
@login_required
def admin_navigation():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            item = NavigationItem(
                label=request.form.get("label"),
                url=request.form.get("url"),
                is_external=bool(request.form.get("is_external")),
                is_cta=bool(request.form.get("is_cta")),
                order=int(request.form.get("order") or 0),
                is_visible=True,
            )
            db.session.add(item)
            db.session.commit()
            flash("Menu item added.", "success")
        elif action == "delete":
            item = NavigationItem.query.get(request.form.get("id"))
            if item:
                db.session.delete(item)
                db.session.commit()
                flash("Menu item deleted.", "success")
        return redirect(url_for("admin_navigation"))
    items = NavigationItem.query.order_by(NavigationItem.order).all()
    return render_template("admin/navigation.html", items=items)


# ---------- ADMIN: PRICING ----------

@app.route("/admin/pricing")
@login_required
def admin_pricing():
    plans = PricingPlan.query.order_by(PricingPlan.order).all()
    return render_template("admin/pricing.html", plans=plans)


@app.route("/admin/pricing/new", methods=["GET", "POST"])
@login_required
def admin_pricing_new():
    if request.method == "POST":
        plan = PricingPlan(
            name=request.form.get("name"),
            price=request.form.get("price"),
            currency=request.form.get("currency") or "NPR",
            description=request.form.get("description"),
            features=[f.strip() for f in request.form.get("features", "").split("\n") if f.strip()],
            button_text=request.form.get("button_text") or "Get Started",
            button_url=request.form.get("button_url") or "/contact",
            is_featured=bool(request.form.get("is_featured")),
            badge=request.form.get("badge"),
            order=int(request.form.get("order") or 0),
            is_visible=bool(request.form.get("is_visible")),
        )
        db.session.add(plan)
        db.session.commit()
        flash("Plan created.", "success")
        return redirect(url_for("admin_pricing"))
    return render_template("admin/pricing_form.html", plan=None)


@app.route("/admin/pricing/<int:pid>/edit", methods=["GET", "POST"])
@login_required
def admin_pricing_edit(pid):
    plan = PricingPlan.query.get_or_404(pid)
    if request.method == "POST":
        plan.name = request.form.get("name")
        plan.price = request.form.get("price")
        plan.currency = request.form.get("currency") or "NPR"
        plan.description = request.form.get("description")
        plan.features = [f.strip() for f in request.form.get("features", "").split("\n") if f.strip()]
        plan.button_text = request.form.get("button_text") or "Get Started"
        plan.button_url = request.form.get("button_url") or "/contact"
        plan.is_featured = bool(request.form.get("is_featured"))
        plan.badge = request.form.get("badge")
        plan.order = int(request.form.get("order") or 0)
        plan.is_visible = bool(request.form.get("is_visible"))
        db.session.commit()
        flash("Plan updated.", "success")
        return redirect(url_for("admin_pricing"))
    return render_template("admin/pricing_form.html", plan=plan)


# ---------- ADMIN: TEAM ----------

@app.route("/admin/team")
@login_required
def admin_team():
    members = TeamMember.query.order_by(TeamMember.order).all()
    return render_template("admin/team.html", members=members)


@app.route("/admin/team/new", methods=["GET", "POST"])
@login_required
def admin_team_new():
    if request.method == "POST":
        m = TeamMember(
            name=request.form.get("name"),
            position=request.form.get("position"),
            bio=request.form.get("bio"),
            photo=request.form.get("photo"),
            email=request.form.get("email"),
            skills=[s.strip() for s in request.form.get("skills", "").split(",") if s.strip()],
            order=int(request.form.get("order") or 0),
            is_visible=bool(request.form.get("is_visible")),
        )
        db.session.add(m)
        db.session.commit()
        flash("Team member added.", "success")
        return redirect(url_for("admin_team"))
    return render_template("admin/team_form.html", member=None)


@app.route("/admin/team/<int:mid>/edit", methods=["GET", "POST"])
@login_required
def admin_team_edit(mid):
    member = TeamMember.query.get_or_404(mid)
    if request.method == "POST":
        member.name = request.form.get("name")
        member.position = request.form.get("position")
        member.bio = request.form.get("bio")
        member.photo = request.form.get("photo")
        member.email = request.form.get("email")
        member.skills = [s.strip() for s in request.form.get("skills", "").split(",") if s.strip()]
        member.order = int(request.form.get("order") or 0)
        member.is_visible = bool(request.form.get("is_visible"))
        db.session.commit()
        flash("Team member updated.", "success")
        return redirect(url_for("admin_team"))
    return render_template("admin/team_form.html", member=member)


# ---------- ADMIN: PARTNERSHIPS ----------

@app.route("/admin/partnerships")
@login_required
def admin_partnerships():
    items = Partnership.query.order_by(Partnership.order).all()
    return render_template("admin/partnerships.html", items=items)


@app.route("/admin/partnerships/new", methods=["GET", "POST"])
@login_required
def admin_partnership_new():
    if request.method == "POST":
        p = Partnership(
            partner_name=request.form.get("partner_name"),
            partner_logo=request.form.get("partner_logo"),
            partner_url=request.form.get("partner_url"),
            badge_text=request.form.get("badge_text"),
            description=request.form.get("description"),
            is_featured=bool(request.form.get("is_featured")),
            is_visible=bool(request.form.get("is_visible")),
            order=int(request.form.get("order") or 0),
        )
        db.session.add(p)
        db.session.commit()
        flash("Partnership added.", "success")
        return redirect(url_for("admin_partnerships"))
    return render_template("admin/partnership_form.html", item=None)



@app.route("/admin/partnerships/<int:pid>/edit", methods=["GET", "POST"])
@login_required
def admin_partnership_edit(pid):
    item = Partnership.query.get_or_404(pid)
    if request.method == "POST":
        item.partner_name = request.form.get("partner_name", "").strip()
        item.partner_logo = request.form.get("partner_logo")
        item.partner_url = request.form.get("partner_url")
        item.badge_text = request.form.get("badge_text")
        item.description = request.form.get("description")
        item.is_featured = bool(request.form.get("is_featured"))
        item.is_visible = bool(request.form.get("is_visible"))
        item.order = int(request.form.get("order") or 0)
        db.session.commit()
        flash("Partnership updated.", "success")
        return redirect(url_for("admin_partnerships"))
    return render_template("admin/partnership_form.html", item=item)

# ---------- ADMIN: MEDIA (Cloudinary) ----------

@app.route("/admin/media", methods=["GET", "POST"])
@login_required
def admin_media():
    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if file and file.filename:
            try:
                result = cloudinary.uploader.upload(file, folder="bam-studio")
                media = Media(
                    filename=file.filename,
                    url=result["secure_url"],
                    public_id=result["public_id"],
                    resource_type=result.get("resource_type", "image"),
                    size=result.get("bytes"),
                )
                db.session.add(media)
                db.session.commit()
                flash("Uploaded successfully.", "success")
            except Exception as e:
                flash(f"Upload failed: {e}", "error")
        return redirect(url_for("admin_media"))
    media = Media.query.order_by(Media.created_at.desc()).all()
    return render_template("admin/media.html", media=media)



# ---------- ADMIN: SOLUTIONS ----------

@app.route("/admin/solutions")
@login_required
def admin_solutions():
    items = Solution.query.order_by(Solution.order).all()
    return render_template("admin/solutions.html", items=items)


@app.route("/admin/solutions/new", methods=["GET", "POST"])
@login_required
def admin_solution_new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        s = Solution(
            title=title,
            slug=request.form.get("slug") or slugify(title),
            industry=request.form.get("industry"),
            icon=request.form.get("icon"),
            short_description=request.form.get("short_description"),
            problem=request.form.get("problem"),
            solution_text=request.form.get("solution_text"),
            features=[f.strip() for f in request.form.get("features", "").split("\n") if f.strip()],
            technologies=[t.strip() for t in request.form.get("technologies", "").split(",") if t.strip()],
            cta_text=request.form.get("cta_text") or "Discuss this solution",
            cta_url=request.form.get("cta_url") or "/quote",
            order=int(request.form.get("order") or 0),
            is_visible=bool(request.form.get("is_visible")),
        )
        db.session.add(s)
        db.session.commit()
        flash("Solution created.", "success")
        return redirect(url_for("admin_solutions"))
    return render_template("admin/solution_form.html", item=None)


@app.route("/admin/solutions/<int:sid>/edit", methods=["GET", "POST"])
@login_required
def admin_solution_edit(sid):
    item = Solution.query.get_or_404(sid)
    if request.method == "POST":
        item.title = request.form.get("title", "").strip()
        item.slug = request.form.get("slug") or slugify(item.title)
        item.industry = request.form.get("industry")
        item.icon = request.form.get("icon")
        item.short_description = request.form.get("short_description")
        item.problem = request.form.get("problem")
        item.solution_text = request.form.get("solution_text")
        item.features = [f.strip() for f in request.form.get("features", "").split("\n") if f.strip()]
        item.technologies = [t.strip() for t in request.form.get("technologies", "").split(",") if t.strip()]
        item.cta_text = request.form.get("cta_text") or "Discuss this solution"
        item.cta_url = request.form.get("cta_url") or "/quote"
        item.order = int(request.form.get("order") or 0)
        item.is_visible = bool(request.form.get("is_visible"))
        db.session.commit()
        flash("Solution updated.", "success")
        return redirect(url_for("admin_solutions"))
    return render_template("admin/solution_form.html", item=item)


# ---------- ADMIN: PROCESS ----------

@app.route("/admin/process")
@login_required
def admin_process():
    items = ProcessStep.query.order_by(ProcessStep.order).all()
    return render_template("admin/process.html", items=items)


@app.route("/admin/process/new", methods=["GET", "POST"])
@login_required
def admin_process_new():
    if request.method == "POST":
        s = ProcessStep(
            step_number=int(request.form.get("step_number") or 1),
            title=request.form.get("title", "").strip(),
            what_happens=request.form.get("what_happens"),
            client_provides=request.form.get("client_provides"),
            bam_delivers=request.form.get("bam_delivers"),
            order=int(request.form.get("order") or 0),
            is_visible=bool(request.form.get("is_visible")),
        )
        db.session.add(s)
        db.session.commit()
        flash("Step created.", "success")
        return redirect(url_for("admin_process"))
    return render_template("admin/process_form.html", item=None)


@app.route("/admin/process/<int:sid>/edit", methods=["GET", "POST"])
@login_required
def admin_process_edit(sid):
    item = ProcessStep.query.get_or_404(sid)
    if request.method == "POST":
        item.step_number = int(request.form.get("step_number") or 1)
        item.title = request.form.get("title", "").strip()
        item.what_happens = request.form.get("what_happens")
        item.client_provides = request.form.get("client_provides")
        item.bam_delivers = request.form.get("bam_delivers")
        item.order = int(request.form.get("order") or 0)
        item.is_visible = bool(request.form.get("is_visible"))
        db.session.commit()
        flash("Step updated.", "success")
        return redirect(url_for("admin_process"))
    return render_template("admin/process_form.html", item=item)


# ---------- ADMIN: FAQ ----------

@app.route("/admin/faqs")
@login_required
def admin_faqs():
    items = FAQ.query.order_by(FAQ.order).all()
    return render_template("admin/faqs.html", items=items)


@app.route("/admin/faqs/new", methods=["GET", "POST"])
@login_required
def admin_faq_new():
    if request.method == "POST":
        f = FAQ(
            question=request.form.get("question", "").strip(),
            answer=request.form.get("answer", "").strip(),
            category=request.form.get("category") or "General",
            order=int(request.form.get("order") or 0),
            is_visible=bool(request.form.get("is_visible")),
        )
        db.session.add(f)
        db.session.commit()
        flash("FAQ created.", "success")
        return redirect(url_for("admin_faqs"))
    return render_template("admin/faq_form.html", item=None)


@app.route("/admin/faqs/<int:fid>/edit", methods=["GET", "POST"])
@login_required
def admin_faq_edit(fid):
    item = FAQ.query.get_or_404(fid)
    if request.method == "POST":
        item.question = request.form.get("question", "").strip()
        item.answer = request.form.get("answer", "").strip()
        item.category = request.form.get("category") or "General"
        item.order = int(request.form.get("order") or 0)
        item.is_visible = bool(request.form.get("is_visible"))
        db.session.commit()
        flash("FAQ updated.", "success")
        return redirect(url_for("admin_faqs"))
    return render_template("admin/faq_form.html", item=item)


# ---------- ADMIN: TESTIMONIALS ----------

@app.route("/admin/testimonials")
@login_required
def admin_testimonials():
    items = Testimonial.query.order_by(Testimonial.order).all()
    return render_template("admin/testimonials.html", items=items)


@app.route("/admin/testimonials/new", methods=["GET", "POST"])
@login_required
def admin_testimonial_new():
    if request.method == "POST":
        t = Testimonial(
            client_name=request.form.get("client_name", "").strip(),
            company=request.form.get("company"),
            role=request.form.get("role"),
            photo=request.form.get("photo"),
            content=request.form.get("content", "").strip(),
            rating=int(request.form.get("rating") or 5),
            project_name=request.form.get("project_name"),
            testimonial_date=request.form.get("testimonial_date"),
            order=int(request.form.get("order") or 0),
            is_published=bool(request.form.get("is_published")),
        )
        db.session.add(t)
        db.session.commit()
        flash("Testimonial created.", "success")
        return redirect(url_for("admin_testimonials"))
    return render_template("admin/testimonial_form.html", item=None)


@app.route("/admin/testimonials/<int:tid>/edit", methods=["GET", "POST"])
@login_required
def admin_testimonial_edit(tid):
    item = Testimonial.query.get_or_404(tid)
    if request.method == "POST":
        item.client_name = request.form.get("client_name", "").strip()
        item.company = request.form.get("company")
        item.role = request.form.get("role")
        item.photo = request.form.get("photo")
        item.content = request.form.get("content", "").strip()
        item.rating = int(request.form.get("rating") or 5)
        item.project_name = request.form.get("project_name")
        item.testimonial_date = request.form.get("testimonial_date")
        item.order = int(request.form.get("order") or 0)
        item.is_published = bool(request.form.get("is_published"))
        db.session.commit()
        flash("Testimonial updated.", "success")
        return redirect(url_for("admin_testimonials"))
    return render_template("admin/testimonial_form.html", item=item)


# ---------- ADMIN: STATS & VALUES ----------

@app.route("/admin/stats")
@login_required
def admin_stats():
    stats = SiteStat.query.order_by(SiteStat.order).all()
    values = ValueItem.query.order_by(ValueItem.order).all()
    return render_template("admin/stats.html", stats=stats, values=values)


@app.route("/admin/stats/add", methods=["POST"])
@login_required
def admin_stat_add():
    db.session.add(SiteStat(
        value=request.form.get("value", "").strip(),
        label=request.form.get("label", "").strip(),
        order=int(request.form.get("order") or 0),
        is_visible=True,
    ))
    db.session.commit()
    flash("Stat added.", "success")
    return redirect(url_for("admin_stats"))


@app.route("/admin/stats/<int:sid>/delete", methods=["POST"])
@login_required
def admin_stat_delete(sid):
    s = SiteStat.query.get_or_404(sid)
    db.session.delete(s)
    db.session.commit()
    flash("Stat deleted.", "success")
    return redirect(url_for("admin_stats"))


@app.route("/admin/values/add", methods=["POST"])
@login_required
def admin_value_add():
    db.session.add(ValueItem(
        title=request.form.get("title", "").strip(),
        description=request.form.get("description"),
        order=int(request.form.get("order") or 0),
        is_visible=True,
    ))
    db.session.commit()
    flash("Value added.", "success")
    return redirect(url_for("admin_stats"))


@app.route("/admin/values/<int:vid>/delete", methods=["POST"])
@login_required
def admin_value_delete(vid):
    v = ValueItem.query.get_or_404(vid)
    db.session.delete(v)
    db.session.commit()
    flash("Value deleted.", "success")
    return redirect(url_for("admin_stats"))



# ---------- ADMIN: UPLOAD ----------

@app.route("/admin/upload", methods=["POST"])
@login_required
def admin_upload():
    """Upload image to Cloudinary (or local static if Cloudinary not configured). Returns JSON {url}."""
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": "Empty file"}), 400
    folder = request.form.get("folder") or "bam-studio"
    try:
        if app.config.get("CLOUDINARY_CLOUD_NAME"):
            result = cloudinary.uploader.upload(file, folder=folder)
            url = result["secure_url"]
            media = Media(
                filename=file.filename,
                url=url,
                public_id=result.get("public_id"),
                resource_type=result.get("resource_type", "image"),
                size=result.get("bytes"),
                folder=folder,
            )
            db.session.add(media)
            db.session.commit()
            return jsonify({"url": url, "public_id": result.get("public_id")})
        else:
            # Local fallback
            import os
            from werkzeug.utils import secure_filename
            os.makedirs(os.path.join(app.root_path, "static", "uploads"), exist_ok=True)
            fname = secure_filename(file.filename)
            path = os.path.join(app.root_path, "static", "uploads", fname)
            file.save(path)
            url = url_for("static", filename=f"uploads/{fname}")
            media = Media(filename=fname, url=url, resource_type="image", folder="local")
            db.session.add(media)
            db.session.commit()
            return jsonify({"url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ---------- ADMIN: CAREERS ----------

@app.route("/admin/jobs")
@login_required
def admin_jobs():
    items = JobPosition.query.order_by(JobPosition.order).all()
    return render_template("admin/jobs.html", items=items)


@app.route("/admin/jobs/new", methods=["GET", "POST"])
@login_required
def admin_job_new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        j = JobPosition(
            title=title,
            slug=request.form.get("slug") or slugify(title),
            department=request.form.get("department"),
            employment_type=request.form.get("employment_type"),
            location=request.form.get("location") or "Nepal",
            work_mode=request.form.get("work_mode"),
            experience=request.form.get("experience"),
            salary=request.form.get("salary"),
            deadline=request.form.get("deadline"),
            overview=request.form.get("overview"),
            about_role=request.form.get("about_role"),
            responsibilities=[x.strip() for x in request.form.get("responsibilities", "").split("\n") if x.strip()],
            requirements=[x.strip() for x in request.form.get("requirements", "").split("\n") if x.strip()],
            nice_to_have=[x.strip() for x in request.form.get("nice_to_have", "").split("\n") if x.strip()],
            what_we_offer=[x.strip() for x in request.form.get("what_we_offer", "").split("\n") if x.strip()],
            is_internship=bool(request.form.get("is_internship")),
            is_freelance=bool(request.form.get("is_freelance")),
            duration=request.form.get("duration"),
            is_published=bool(request.form.get("is_published")),
            is_closed=bool(request.form.get("is_closed")),
            order=int(request.form.get("order") or 0),
        )
        db.session.add(j)
        db.session.commit()
        flash("Position created.", "success")
        return redirect(url_for("admin_jobs"))
    return render_template("admin/job_form.html", item=None)


@app.route("/admin/jobs/<int:jid>/edit", methods=["GET", "POST"])
@login_required
def admin_job_edit(jid):
    item = JobPosition.query.get_or_404(jid)
    if request.method == "POST":
        item.title = request.form.get("title", "").strip()
        item.slug = request.form.get("slug") or slugify(item.title)
        item.department = request.form.get("department")
        item.employment_type = request.form.get("employment_type")
        item.location = request.form.get("location") or "Nepal"
        item.work_mode = request.form.get("work_mode")
        item.experience = request.form.get("experience")
        item.salary = request.form.get("salary")
        item.deadline = request.form.get("deadline")
        item.overview = request.form.get("overview")
        item.about_role = request.form.get("about_role")
        item.responsibilities = [x.strip() for x in request.form.get("responsibilities", "").split("\n") if x.strip()]
        item.requirements = [x.strip() for x in request.form.get("requirements", "").split("\n") if x.strip()]
        item.nice_to_have = [x.strip() for x in request.form.get("nice_to_have", "").split("\n") if x.strip()]
        item.what_we_offer = [x.strip() for x in request.form.get("what_we_offer", "").split("\n") if x.strip()]
        item.is_internship = bool(request.form.get("is_internship"))
        item.is_freelance = bool(request.form.get("is_freelance"))
        item.duration = request.form.get("duration")
        item.is_published = bool(request.form.get("is_published"))
        item.is_closed = bool(request.form.get("is_closed"))
        item.order = int(request.form.get("order") or 0)
        db.session.commit()
        flash("Position updated.", "success")
        return redirect(url_for("admin_jobs"))
    return render_template("admin/job_form.html", item=item)


@app.route("/admin/jobs/<int:jid>/delete", methods=["POST"])
@login_required
def admin_job_delete(jid):
    item = JobPosition.query.get_or_404(jid)
    db.session.delete(item)
    db.session.commit()
    flash("Position deleted.", "success")
    return redirect(url_for("admin_jobs"))


@app.route("/admin/applications")
@login_required
def admin_applications():
    status = request.args.get("status")
    q = JobApplication.query
    if status:
        q = q.filter_by(status=status)
    items = q.order_by(JobApplication.created_at.desc()).all()
    return render_template("admin/applications.html", items=items, current_status=status)


@app.route("/admin/applications/<int:aid>", methods=["GET", "POST"])
@login_required
def admin_application_detail(aid):
    item = JobApplication.query.get_or_404(aid)
    if request.method == "POST":
        item.status = request.form.get("status", item.status)
        item.notes = request.form.get("notes", item.notes)
        db.session.commit()
        flash("Application updated.", "success")
        return redirect(url_for("admin_application_detail", aid=aid))
    return render_template("admin/application_detail.html", item=item)


# ---------- CLI / INIT ----------

@app.cli.command("init-db")
def init_db():
    """Create tables."""
    db.create_all()
    print("Database tables created.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
