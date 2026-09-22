from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), default="Admin")
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SiteSetting(db.Model):
    __tablename__ = "site_settings"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ThemeSetting(db.Model):
    __tablename__ = "theme_settings"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NavigationItem(db.Model):
    __tablename__ = "navigation_items"
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    is_external = db.Column(db.Boolean, default=False)
    is_cta = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("navigation_items.id"), nullable=True)


class HomepageSection(db.Model):
    __tablename__ = "homepage_sections"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(300))
    content = db.Column(db.Text)
    is_visible = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    extra_data = db.Column(db.JSON, default=dict)


class ProjectCategory(db.Model):
    __tablename__ = "project_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("project_categories.id"))
    client = db.Column(db.String(150))
    short_description = db.Column(db.Text)
    full_description = db.Column(db.Text)
    industry = db.Column(db.String(100))
    year = db.Column(db.String(20))
    services_used = db.Column(db.JSON, default=list)
    challenge = db.Column(db.Text)
    solution = db.Column(db.Text)
    features = db.Column(db.JSON, default=list)
    technologies = db.Column(db.JSON, default=list)
    results = db.Column(db.Text)
    cover_image = db.Column(db.String(500))
    live_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    project_date = db.Column(db.String(50))
    location = db.Column(db.String(100))
    is_featured = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship("ProjectCategory", backref="projects")
    images = db.relationship("ProjectImage", backref="project", cascade="all, delete-orphan", order_by="ProjectImage.order")


class ProjectImage(db.Model):
    __tablename__ = "project_images"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(255))
    caption = db.Column(db.String(255))
    order = db.Column(db.Integer, default=0)


class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(170), unique=True, nullable=False)
    description = db.Column(db.Text)  # short
    full_description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    image = db.Column(db.String(500))
    features = db.Column(db.JSON, default=list)
    technologies = db.Column(db.JSON, default=list)
    deliverables = db.Column(db.JSON, default=list)
    timeline = db.Column(db.String(100))
    starting_price = db.Column(db.String(50))
    currency = db.Column(db.String(10), default="NPR")
    cta_text = db.Column(db.String(100), default="Get a Quote")
    cta_url = db.Column(db.String(255), default="/contact")
    order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)


class PricingPlan(db.Model):
    __tablename__ = "pricing_plans"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50))
    currency = db.Column(db.String(10), default="NPR")
    starting_from = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)
    features = db.Column(db.JSON, default=list)
    button_text = db.Column(db.String(100), default="Get Started")
    button_url = db.Column(db.String(255), default="/contact")
    is_featured = db.Column(db.Boolean, default=False)
    badge = db.Column(db.String(50))
    order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)


class TeamMember(db.Model):
    __tablename__ = "team_members"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(150))
    bio = db.Column(db.Text)
    photo = db.Column(db.String(500))
    email = db.Column(db.String(120))
    social_links = db.Column(db.JSON, default=dict)
    skills = db.Column(db.JSON, default=list)
    order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)


class Partnership(db.Model):
    __tablename__ = "partnerships"
    id = db.Column(db.Integer, primary_key=True)
    partner_name = db.Column(db.String(150), nullable=False)
    partner_logo = db.Column(db.String(500))
    partner_url = db.Column(db.String(500))
    badge_text = db.Column(db.String(150))
    description = db.Column(db.Text)
    start_date = db.Column(db.String(50))
    is_featured = db.Column(db.Boolean, default=False)
    is_visible = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)


class Testimonial(db.Model):
    __tablename__ = "testimonials"
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(150))
    role = db.Column(db.String(100))
    photo = db.Column(db.String(500))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    project_name = db.Column(db.String(150))
    testimonial_date = db.Column(db.String(50))
    order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)


class BlogCategory(db.Model):
    __tablename__ = "blog_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(280), unique=True, nullable=False, index=True)
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text)
    featured_image = db.Column(db.String(500))
    category_id = db.Column(db.Integer, db.ForeignKey("blog_categories.id"))
    tags = db.Column(db.JSON, default=list)
    author = db.Column(db.String(100), default="BAM Studio")
    reading_time = db.Column(db.String(20), default="5 min")
    seo_title = db.Column(db.String(255))
    seo_description = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="draft")  # draft, published, scheduled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship("BlogCategory", backref="posts")


class Lead(db.Model):
    __tablename__ = "leads"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50))
    company = db.Column(db.String(150))
    service = db.Column(db.String(100))
    budget = db.Column(db.String(50))
    message = db.Column(db.Text)
    status = db.Column(db.String(30), default="NEW")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Media(db.Model):
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(255))
    resource_type = db.Column(db.String(50), default="image")
    alt_text = db.Column(db.String(255))
    folder = db.Column(db.String(100))
    size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SocialLink(db.Model):
    __tablename__ = "social_links"
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), unique=True, nullable=False)
    url = db.Column(db.String(500))
    is_visible = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)


class SEOSetting(db.Model):
    __tablename__ = "seo_settings"
    id = db.Column(db.Integer, primary_key=True)
    page_key = db.Column(db.String(100), unique=True, nullable=False)  # global or page slug
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    keywords = db.Column(db.Text)
    og_title = db.Column(db.String(255))
    og_description = db.Column(db.Text)
    og_image = db.Column(db.String(500))
    canonical_url = db.Column(db.String(500))
    noindex = db.Column(db.Boolean, default=False)


class Solution(db.Model):
    __tablename__ = "solutions"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(170), unique=True, nullable=False)
    industry = db.Column(db.String(100))
    icon = db.Column(db.String(50))
    short_description = db.Column(db.Text)
    problem = db.Column(db.Text)
    solution_text = db.Column(db.Text)
    features = db.Column(db.JSON, default=list)
    technologies = db.Column(db.JSON, default=list)
    image = db.Column(db.String(500))
    cta_text = db.Column(db.String(100), default="Discuss this solution")
    cta_url = db.Column(db.String(255), default="/contact")
    order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)


class ProcessStep(db.Model):
    __tablename__ = "process_steps"
    id = db.Column(db.Integer, primary_key=True)
    step_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    what_happens = db.Column(db.Text)
    client_provides = db.Column(db.Text)
    bam_delivers = db.Column(db.Text)
    icon = db.Column(db.String(50))
    order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)


class FAQ(db.Model):
    __tablename__ = "faqs"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default="General")
    order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)


class SiteStat(db.Model):
    __tablename__ = "site_stats"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)


class ValueItem(db.Model):
    __tablename__ = "value_items"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)


class JobPosition(db.Model):
    __tablename__ = "job_positions"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(170), unique=True, nullable=False, index=True)
    department = db.Column(db.String(100))
    employment_type = db.Column(db.String(80))  # Full-time / Part-time / Internship / Freelance
    location = db.Column(db.String(120), default="Nepal")
    work_mode = db.Column(db.String(80))  # Remote / On-site / Hybrid
    experience = db.Column(db.String(80))
    salary = db.Column(db.String(120))
    deadline = db.Column(db.String(50))
    overview = db.Column(db.Text)
    about_role = db.Column(db.Text)
    responsibilities = db.Column(db.JSON, default=list)
    requirements = db.Column(db.JSON, default=list)
    nice_to_have = db.Column(db.JSON, default=list)
    what_we_offer = db.Column(db.JSON, default=list)
    is_internship = db.Column(db.Boolean, default=False)
    is_freelance = db.Column(db.Boolean, default=False)
    duration = db.Column(db.String(80))  # for internships
    is_published = db.Column(db.Boolean, default=True)
    is_closed = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class JobApplication(db.Model):
    __tablename__ = "job_applications"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50))
    position_id = db.Column(db.Integer, db.ForeignKey("job_positions.id"), nullable=True)
    position_title = db.Column(db.String(150))  # snapshot / general
    experience = db.Column(db.String(50))
    portfolio = db.Column(db.String(500))
    github = db.Column(db.String(500))
    linkedin = db.Column(db.String(500))
    cover_letter = db.Column(db.Text)
    resume_url = db.Column(db.String(500))
    expertise = db.Column(db.String(150))  # general application
    message = db.Column(db.Text)
    application_type = db.Column(db.String(30), default="job")  # job / internship / freelance / general
    status = db.Column(db.String(30), default="NEW")  # NEW, REVIEWING, SHORTLISTED, INTERVIEW, SELECTED, REJECTED
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    position = db.relationship("JobPosition", backref="applications")
