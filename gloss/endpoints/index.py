"""Render landing page."""

from flask import Blueprint, render_template, request
from flask.ext.login import login_required

from gloss import db, models, searchengine
from gloss.config import config


index_blueprint = Blueprint('index',
                            __name__,
                            url_prefix=config.get('url', 'base'))


MAX_PER_PAGE = 10


@index_blueprint.route('/', methods=['GET'])
@login_required
def render_index_page():
    """Render index page."""
    keyword = request.args.get('q')
    cursor = int(request.args.get('c', 0))
    labels = db.session.query(models.Label)\
        .order_by(models.Label.name)\
        .all()
    if not keyword:
        glosses = db.session.query(models.Gloss)\
            .filter((models.Gloss.archive == False))\
            .order_by(models.Gloss.timestamp.desc())\
            .all()
    elif keyword == 'all':
        glosses = db.session.query(models.Gloss)\
            .order_by(models.Gloss.timestamp.desc())\
            .all()
    # E.g. the label search for "ai": "?q=label.ai".
    elif keyword.startswith('label.'):
        label_name = keyword.split('.')[1]
        glosses = db.session.query(models.Gloss)\
            .join(models.Label, models.Gloss.labels)\
            .filter(models.Label.name == label_name)\
            .order_by(models.Gloss.timestamp.desc())\
            .all()
        labels = db.session.query(models.Label).all()
    else:
        glosses = searchengine.find_glosses_by_keyword(keyword)

    if len(glosses) > MAX_PER_PAGE:
        c_prev = max(0, cursor - MAX_PER_PAGE)
        if len(glosses) - cursor <= MAX_PER_PAGE:
            c_next = None
        else:
            c_next = cursor + MAX_PER_PAGE
        glosses = glosses[cursor: cursor+MAX_PER_PAGE]
    else:
        c_prev = c_next = None
    return render_template('index.html', glosses=glosses, labels=labels,
                           q=keyword, c_prev=c_prev, c_next=c_next)
