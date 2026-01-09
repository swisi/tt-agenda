from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from urllib.parse import urljoin, urlparse
from ..models import User
from ..extensions import db
import requests
from ..config import Config
import logging

bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            flash('Erfolgreich angemeldet!', 'success')
            next_page = request.args.get('next')
            if next_page and not is_safe_url(next_page):
                next_page = None
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Ungültiger Benutzername oder Passwort.', 'danger')

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Sie wurden abgemeldet.', 'info')
    return redirect(url_for('auth.login'))
