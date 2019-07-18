import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('board', __name__)


@bp.route('/')
def index():
    db = get_db()
    cards = db.execute(
        'SELECT c.id, title,  created'
        ' FROM cards c'
        ' ORDER BY created DESC'
    ).fetchall()
    tasks = db.execute(
        'SELECT t.id, body, created, pcard'
        ' FROM tasks t'
        ' ORDER BY created ASC'
    ).fetchall()
    cdata = []
    tdata = []
    for c in cards:
        cdata.append([x for x in c])
    for t in tasks:
        tdata.append([x for x in t])
    # return render_template('blog/index.html', cards=cards, tasks=tasks)
    print(cdata, tdata)
    # return (cards, tasks)
    return render_template('board/index.html', cards=cards, tasks=tasks)


@bp.route('/addCard', methods=('GET', 'POST'))
@login_required
def addCard():
    if request.method == 'POST':
        title = request.form['title']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO cards (title)'
                ' VALUES (?)',
                (title,)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/addCard.html')


@bp.route('/<int:id>/addTask', methods=('GET', 'POST'))
@login_required
def addTask(id):
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'Body is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tasks (pcard, body)'
                ' VALUES (?, ?)',
                (id, body)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/addTask.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
