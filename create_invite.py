import sys
from flask import url_for
from action import app
from action.models import AdminInvite, db


def create_invite(email):
    with app.app_context():
        invite = AdminInvite(email)
        db.session.add(invite)
        db.session.commit()
        invite_id = invite.id
        url = url_for('admin.register', invite_id=invite_id)
    return url


if __name__ == '__main__':
    email = sys.argv[1]
    invite_url = create_invite(email)
    print(invite_url)
