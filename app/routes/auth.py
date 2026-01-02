from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..models import User
from ..extensions import db

bp = Blueprint('auth', __name__)

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
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Ungültiger Benutzername oder Passwort.', 'danger')

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Sie wurden abgemeldet.', 'info')
    return redirect(url_for('auth.login'))
