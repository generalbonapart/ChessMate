import connexion
import six

from swagger_server.models.game_params import GameParams  # noqa: E501
from swagger_server import util
from swagger_server.lichess_api import launch_game, get_game_moves, add_user_move
import pprint
def get_moves_get():  # noqa: E501
    """get_moves_get

    Returns all moves done in the current game. # noqa: E501


    :rtype: List[str]
    """
    game = get_game_moves()
    #pprint.pprint(game, indent=3)
    return game


def make_move_move_put(move):  # noqa: E501
    """make_move_move_put

    Make a move in a game # noqa: E501

    :param move: chess move in scientific notation
    :type move: str

    :rtype: None
    """
    add_user_move(move)
    return util.SUCCESS


def start_game_put(body):  # noqa: E501
    """start_game_put

    Start game with the settings provided # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = GameParams.from_dict(connexion.request.get_json())  # noqa: E501
        launch_game(body)
    return util.SUCCESS
