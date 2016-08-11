import simplejson as json

from flask import request, Response, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from FlowrouteMessagingLib.Models.Message import Message

from sms_poll.settings import POLL_NUMBER, HEADER, HACK_IDS
from sms_poll.database import db_session
from sms_poll.log import log
from sms_poll.models import Vote
from sms_poll.app import create_app


app = create_app()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


class InternalSMSDispatcherError(Exception):
    def __init__(self, message, status_code=500, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or())
        rv['message'] = self.message
        return rv


def send_message(recipients, virtual_tn, msg, is_system_msg=False):
    """
    For each recipient, passes a Message to Flowroute's messaging controller.
    The message will be sent from the 'virtual_tn' number. If this is a system
    message, the message body will be prefixed with the org name for context.
    If an exception is raised by the controller, an error is logged, and an
    internal error is raised with the exception content.
    """
    if is_system_msg:
        msg = "[{}]: {}".format(HEADER.upper(), msg)
    for recipient in recipients:
        message = Message(
            to=recipient,
            from_=virtual_tn,
            content=msg)
        try:
            app.sms_controller.create_message(message)
        except Exception as e:
            strerr = vars(e).get('response_body', None)
            log.critical({"message": "Raised an exception sending SMS",
                          "status": "failed",
                          "exc": e,
                          "strerr": vars(e).get('response_body', None)})
            raise InternalSMSDispatcherError(
                "An error occured when requesting against Flowroute's API.",
                payload={"strerr": strerr,
                         "reason": "InternalSMSDispatcherError"})
        else:
            log.info({"message": "Message sent to {}".format(recipient),
                      "status": "succeeded"})


class InvalidAPIUsage(Exception):
    """
    A generic exception for invalid API interactions.
    """
    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or())
        rv['message'] = self.message
        return rv


@app.route("/", methods=['GET'])
def get_stats():
    results = []
    for hack in HACK_IDS:
        try:
            hack_votes = len(Vote.query.filter_by(vote=hack).all())
            results.append((hack, hack_votes))
        except Exception as e:
            log.error({"exc": e})

    results = sorted(results, key=lambda li: li[1])
    return Response(json.dumps(results), content_type="application/json")


def count_vote(voter, vote):
    try:
        new_vote = Vote(voter, vote)
    except IntegrityError:
        prev_vote = Vote.query.filter_by(value=voter).one()
        prev_vote.vote = vote
        db_session.add(prev_vote)
        db_session.commit()
        return "Thanks! Your vote has been changed to hack {}".format(vote)
    else:
        db_session.add(new_vote)
        db_session.commit()
        return "Thanks! Your vote (hack {}) has been recorded.".format(vote)


@app.route("/", methods=['POST'])
def inbound_handler():
    body = request.json
    try:
        virtual_tn = body['to']
        if virtual_tn is not POLL_NUMBER:
            return Response(status=200)
        assert len() <= 18
        voter = body['from']
        assert len(voter) <= 18
        message = body['body']
    except (TypeError, KeyError, AssertionError) as e:
        msg = ("Malformed inbound message: {}".format(body))
        log.error({"message": msg, "status": "failed", "exc": str(e)})
        return Response('There was an issue parsing your request.', status=400)
    vote = ''.join([i for i in message if i.isdigit()])
    if len(vote) == 0:
        send_message(
            [voter], virtual_tn,
            "Sorry, we didn't understand. Please try again and include a number.",
            is_system_msg=True)
    else:
        message = count_vote(voter, int(vote))
        send_message(
            [voter], virtual_tn,
            message,
            is_system_msg=True)
    log.info({"message": msg, "status": "succeeded"})
    return Response(status=200)


@app.errorhandler((InvalidAPIUsage, InternalSMSDispatcherError))
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    response.content_type = 'application/json'
    return response

if __name__ == "__main__":
    app.run('0.0.0.0', 8000)
