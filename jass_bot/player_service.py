import logging

from flask import request
from jass.service.player_service_app import PlayerServiceApp

from rule_based_bot.rule_based_agent import RuleBasedAgent

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('player_service')


def create_app():
    app = PlayerServiceApp('player_service')

    app.add_player('rule', RuleBasedAgent())

    @app.before_request
    def log_request_info():
        logger.info(f"Request: {request.method} {request.url}")
        if request.data:
            logger.debug(f"Request Data: {request.data}")

    @app.route('/lino')
    def bot_route():
        return "Player lino here"

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8888)
