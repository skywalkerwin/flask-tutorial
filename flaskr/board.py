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


def get_task(id):
    task = get_db().execute(
        'SELECT t.id, pcard, created, body, torder'
        ' FROM tasks t'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    return task


@bp.route('/updateTask/<int:cid>/<int:tid>/', methods=('GET', 'POST'))
def updateTask(cid, tid):
    task = get_task(tid)

    if request.method == 'POST':
        body = request.form['body']
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE tasks SET body = ?'
                ' WHERE id = ?',
                (body, tid)
            )
            db.commit()

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
            return redirect(url_for('board.index'))

    return render_template('board/updateTask.html', task=task)


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
        print('TORDER IS: ')
        print(tord)
        num_tasks = db.execute(
            'SELECT num_tasks FROM cards WHERE id=?',
            (cid,)
        ).fetchone()['num_tasks']
        db.execute('DELETE FROM tasks WHERE id = ?', (tid,))
        db.commit()
        db.execute(
            'UPDATE cards SET num_tasks = ?'
            'WHERE id = ?',
            ((num_tasks-1), cid)
        )
        db.commit()
        db.execute(
            'UPDATE tasks SET torder = (torder - 1)'
            'WHERE (torder > ?)',
            (tord,)
        )
        db.commit()
        return redirect(url_for('board.index'))
    else:
        return 'error'
# need to add shifting api calls
