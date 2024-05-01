# app.py

from flask import Flask, request, jsonify, render_template
from game import GameManager
import os
import logging

app = Flask(__name__, template_folder='web')
app.json.sort_keys = False

# Create and configure logger
logging.basicConfig(format='%(asctime)s %(message)s')
 
# Creating an object
logger = logging.getLogger()
 
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

manager = GameManager()

# Serve static files from the 'web' directory
app.static_folder = 'web'
app.static_url_path= '/static'
 
# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

############## GAME MODEL ##############

# Get all game models
@app.route('/game-models', methods=['GET'])
def get_allGameModels():
    return manager.gameController.get_allGameModels(), 200

# Get a game model
@app.route('/game-model/<int:gameModelId>', methods=['GET'])
def get_gameModel(gameModelId: int):
    logger.debug("get_gameModel: gameModelId [%d]", gameModelId)

    return manager.get_gameModel(gameModelId), 200

# Create a game model
@app.route('/game-model', methods=['POST'])
def create_gameModel():
    data = request.get_json()
    logger.debug("create_gameModel: data %s", data)

    name: str = data.get("name")
    cylinders: list = data.get("cylinders")

    return manager.create_model(name, cylinders), 201

# Update a game model
@app.route('/game-model/<int:gameModelId>', methods=['PUT'])
def update_gameModel(gameModelId: int):
    ("update_gameModel: gameModelId [%d]", gameModelId)
    data = request.get_json()
    logger.debug("update_gameModel: data %s", data)

    name: str = data.get("name")
    scoringType: str = data.get("scoring_type")
    cylinders: list = data.get("cylinders")

    return manager.update_model(gameModelId, name, cylinders, scoringType), 201

# Delete game model
@app.route('/game-model/<int:gameModelId>', methods=['DELETE'])
def delete_gameModel(gameModelId: int):
    logger.debug("delete_gameModel: gameModelId [%d]", gameModelId)

    return manager.delete_gameModel(gameModelId), 204

############## GAME ##############

# Get all games
@app.route("/games", methods=['GET'])
def get_allGames():
    return manager.gameController.get_allGames(), 200

# Get a game
@app.route('/game/<int:gameId>', methods=['GET'])
def get_game(gameId: int):
    logger.debug("get_game: gameId [%d]", gameId)

    return manager.get_game(gameId), 200

# Create game
@app.route('/game/<int:gameModelId>', methods=['POST'])
def create_game(gameModelId: int):
    logger.debug("create_game: gameModelId [%d]", gameModelId)
    data = request.get_json()
    logger.debug("create_game: data %s", data)

    name: str = data.get("name") 
    return manager.create_game(gameModelId, name), 201

# Delete a game
@app.route('/game/<int:gameId>', methods=['DELETE'])
def delete_game(gameId: int):
    logger.debug("delete_game: gameId [%d]", gameId)
    return manager.delete_game(gameId), 204

############## TEAM ##############

# Create a team
@app.route('/team', methods=['POST'])
def create_team():
    data = request.get_json()
    logger.debug("create_team: data %s", data)

    name: str = data.get("name")
    gameId: int = data.get("gameId")

    return manager.create_team(name, gameId), 201

# Delete a team
@app.route('/team/<int:teamId>', methods=['DELETE'])
def delete_team(teamId):
    logger.debug("delete_team: teamId [%d]", teamId)
    return manager.delete_team(teamId), 204

# Update team
@app.route('/team/<int:teamId>', methods=['PUT'])
def udpate_team(teamId):
    logger.debug("udpate_team: teamId [%d]", teamId)
    data = request.get_json()
    logger.debug("udpate_team: data %s", data)
    
    name: str = data.get("name")
    gameId: int = data.get("gameId")
    color = data.get("color")

    return manager.udpate_team(teamId, name, gameId, color), 200

############## PLAYER ##############

# Create a player
@app.route('/player', methods=['POST'])
def create_player():
    data = request.get_json()
    logger.debug("create_player: data %s", data)

    name: str = data.get("name")
    teamId: int = data.get("teamId")

    return manager.create_player(name, teamId), 201

# Add a player to a team
@app.route('/player/<int:playerId>', methods=['PUT'])
def update_player(playerId: int):
    logger.debug("update_player: playerId [%d]", playerId)
    data = request.get_json()
    logger.debug("update_player: data %s", data)

    name: str = data.get("name")
    teamId: int = data.get("teamId")

    player = manager.playerController.update(playerId, name, teamId)
    return manager.playerController.to_json(player), 200

# Update player location
@app.route('/player/<int:playerId>/location', methods=['PUT'])
def update_player_location(playerId):
    logger.debug("update_player_location: playerId [%d]", playerId)
    data = request.get_json()
    logger.debug("update_player_location: data %s", data)

    longitude = data.get("longitude")
    latitude = data.get("latitude")
    altitude = data.get("altitude")

    return manager.update_player_location(playerId, latitude, longitude, altitude), 200

@app.errorhandler(400)
def bad_request(ex):
    return jsonify(error=str(ex)), 400

@app.errorhandler(404)
def resource_not_found(ex):
    return jsonify(error=str(ex)), 404

@app.errorhandler(500)
def internal_error(ex):
    return jsonify(error=str(ex)), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5066))
    app.run(debug=True, host='0.0.0.0', port=port)
