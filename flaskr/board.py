import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('board', __name__)


def makedate(dbdate):
    stringdate = dbdate.strftime("%Y-%m-%d")
    return stringdate


@bp.route('/')
def index():
    board = {}
    db = get_db()
    cards = db.execute(
        'SELECT c.id, title,  created'
        ' FROM cards c'
        ' ORDER BY created DESC'
    ).fetchall()
    tasks = db.execute(
        'SELECT t.id, body, created, pcard, torder'
        ' FROM tasks t'
        ' ORDER BY created ASC'
    ).fetchall()
    cdata = []
    tdata = []
    for c in cards:
        cdata.append([x for x in c])
    for t in tasks:
        tdata.append([x for x in t])
    for c in cards:
        board[c['title']] = []
    # return render_template('blog/index.html', cards=cards, tasks=tasks)
    #print(cdata, tdata)
    # print(board)
    # return (board, cards, tasks)
    return render_template('board/index.html', cards=cards, tasks=tasks)


@bp.route('/addCard', methods=('GET', 'POST'))
# @login_required
def addCard():
    print(request.method)
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
                'INSERT INTO cards (title, num_tasks)'
                ' VALUES (?, ?)',
                (title, 0)
            )
            db.commit()
            return redirect(url_for('board.index'))

    return render_template('board/addCard.html')


@bp.route('/<int:id>/addTask', methods=('GET', 'POST'))
# @login_required
def addTask(id):
    print(request.method)
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'Body is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            num_tasks = db.execute(
                'SELECT c.num_tasks FROM cards c WHERE c.id=?',
                (id,)
            ).fetchone()['num_tasks']
            db.execute(
                'UPDATE cards SET num_tasks = ? WHERE id=?',
                ((num_tasks+1), id)
            )
            db.commit()
            db.execute(
                'INSERT INTO tasks (pcard, body, torder) '
                ' VALUES (?, ?, ?)',
                (id, body, num_tasks)
            )
            db.commit()
            return redirect(url_for('board.index'))

    return render_template('board/addTask.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def updateCard(cid):
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
                'UPDATE cards SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, cid)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def updateTask(cid):
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
                'UPDATE card SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, cid)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/deleteTask/<int:cid>/<int:tid>/', methods=('GET', 'POST'))
# @login_required
def deleteTask(cid, tid):
    print(request.method)
    if request.method == 'POST':
        db = get_db()
        tord = db.execute(
            'SELECT torder FROM tasks WHERE id=?',
            (tid,)
        ).fetchone()['torder']
        num_tasks = db.execute(
            'SELECT c.num_tasks FROM cards WHERE id=?',
            (id,)
        ).fetchone()['num_tasks']
        db.execute('DELETE FROM tasks WHERE id = ?', (tid,))
        db.execute(
            'UPDATE cards SET num_task = ?'
            'WHERE id = ?',
            ((num_tasks-1), cid)
        )
        db.execute(
            'UPDATE tasks SET torder = torder - 1'
            'WHERE torder > ?',
            (tord,)
        )
        db.commit()
        return redirect(url_for('board.deleteTask'))
    else:
        return 'error'
