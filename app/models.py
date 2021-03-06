from flask_login.utils import login_required
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from flask_login import UserMixin


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    created_on = db.Column(db.Date, nullable=False, default=date.today())
    sites = db.relationship("Site", cascade="all, delete", backref="user", lazy=True)
    reports = db.relationship("Report", cascade="all, delete", backref="user", lazy=True)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = generate_password_hash(password)

    def __repr__(self):
        return f"User: {self.first_name} {self.last_name} ({self.id})"

report_sites = db.Table('report_sites',
    db.Column('report_id', db.Integer, db.ForeignKey('report.id'), primary_key=True),
    db.Column('site_id', db.Integer, db.ForeignKey('site.id'), primary_key=True)
    )

class Site(db.Model):
    __tablename__ = "site"
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(200), nullable=False)
    gt_global_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    site_updates = db.relationship("SiteUpdate", cascade="all, delete", backref="site", lazy=True)

    def __repr__(self):
        return f"{self.site_name}"

class Report(db.Model):
    __tablename__ = "report"
    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.String(1000))
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    sites = db.relationship('Site', secondary=report_sites, lazy='subquery', backref=db.backref('reports', lazy=True))
    report_updates = db.relationship("ReportUpdate", cascade="all, delete", backref="report", lazy=True)

    def __repr__(self):
        return f"{self.report_name}"

class ReportUpdate(db.Model):
    __tablename__ = "report_update"
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))
    scraped_on = db.Column(db.Date, nullable=False, default=date.today())
    site_updates = db.relationship("SiteUpdate", cascade="all, delete", backref="report_update", lazy=True)

    def __repr__(self):
        return f"Report Name/Report Update ID: {Report.query.filter_by(id=self.report_id).first().name}/{self.id}" 

class SiteUpdate(db.Model):
    __tablename__ = "site_update"
    id = db.Column(db.Integer, primary_key=True)
    report_update_id = db.Column(db.Integer, db.ForeignKey('report_update.id'))
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))
    site_status = db.Column(db.String(250))
    status_changed = db.Column(db.Boolean, default=False)
    new_actions = db.relationship("NewAction", cascade="all, delete", backref="site_update", lazy=True)

    def __repr__(self):
        return f"Site Name/Site Update ID: {Site.query.filter_by(id=self.site_id).first().site_name}/{self.id}"

class NewAction(db.Model):
    __tablename__ = "new_action"
    id = db.Column(db.Integer, primary_key=True)
    site_update_id = db.Column(db.Integer, db.ForeignKey('site_update.id'))
    action_type = db.Column(db.String(300))
    action = db.Column(db.String(300))
    action_date = db.Column(db.String(20))
    received_date = db.Column(db.String(20))
    description = db.Column(db.String(2000))
    new_docs = db.relationship("NewDoc", cascade="all, delete", backref="new_action", lazy=True)

    def __repr__(self):
        return f"New Action ID/Site Update ID: {self.id}/{SiteUpdate.query.filter_by(id=self.site_update_id).first().id}"

class NewDoc(db.Model):
    __tablename__ = "new_doc"
    id = db.Column(db.Integer, primary_key=True)
    new_action_id = db.Column(db.Integer, db.ForeignKey('new_action.id'))
    doc_name = db.Column(db.String(300), nullable=False)
    doc_link = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"New Doc Name/New Action ID: {self.id}/{NewAction.query.filter_by(id=self.new_action_id).first().id}"

