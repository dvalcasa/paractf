# controller.py
from models import Game, Team, Player, Cylinder, LocationHistory, GameType, GameStatus
from repository import GameRepository, TeamRepository, PlayerRepository, LocationHistoryRepository, CylinderRepository
from scoring_models import ScoringFactory, ScoringType
from sqlalchemy.orm import Session
import string, random
from typing import Any
from datetime import datetime, timedelta
from exception import *

class GameController():
    def __init__(self, session: Session):
        self.repository: GameRepository = GameRepository(session)
        self.factory = ScoringFactory()

    # GameModel
    def create_gameModel(self, name: str, cylinders_data: list):
        gameModel: Game = self.repository.create_model(name)
        cylinderController: CylinderController = CylinderController(self.repository.Session)
        [cylinderController.create(gameModel.id, cylinder['latitude'], cylinder['longitude'], cylinder['radius']) for cylinder in cylinders_data]
        return gameModel
    
    def get_allGameModels(self):
        gameModels = self.repository.find_allGameModels()
        return [ self.to_json(game) for game in gameModels ]
    
    def get_gameModel(self, gameModelId: int):
        gameModel: Game = self.repository.find_gameModelById(gameModelId)
        if gameModel is None:
            raise GameModelNotFoundException(f"Game model [{gameModelId}] not found")
        return gameModel

    def update_gameModel(self, gameModelId: int, name: str, cylinders_data: list, scoringTypeStr: str):
        gameModel: Game = self.get_gameModel(gameModelId)

        if name is not None:
            gameModel.name = name

        if scoringTypeStr is not None:
            try:
                scoringType = ScoringType[scoringTypeStr.upper()]
                gameModel.scoringType = scoringType.name
            except Exception:
                raise ScoringTypeNotExistingException(f"ScoringType name [{scoringTypeStr}] does not exit")
        
        if cylinders_data is not None:
            cylinderController: CylinderController = CylinderController(self.repository.Session)
            cylinderController.delete_all(gameModel.cylinders)

            new_cylinders: list[Cylinder] =[]
            for cylinder in cylinders_data:
                new_cylinders.append(cylinderController.create(gameModel.id, cylinder['latitude'], cylinder['longitude'], cylinder['radius']))
            
            gameModel.cylinders = new_cylinders
        
        return self.repository.update(gameModel)
    
    def delete_model(self, gameModelId: int):
        gameModel: Game = self.get_gameModel(gameModelId)
        cylinderController: CylinderController = CylinderController(self.repository.Session)
        cylinderController.delete_all(gameModel.cylinders)
        return self.repository.delete(gameModel)

    # Game
    def set_startDate(self, startDate: datetime):
        return datetime.now() if startDate is None else startDate
    
    def set_endDate(self, endDate: datetime):
        return datetime.now() + timedelta(hours=3) if endDate is None else endDate

    def create_game(self, gameModelId: int, name: str, password: str, startDate: datetime, endDate: datetime):
        gameModel: Game = self.get_gameModel(gameModelId)

        game: Game = self.repository.create_game(name, password, self.set_startDate(startDate), self.set_endDate(endDate), ScoringType[gameModel.scoringType])
        cylinderController: CylinderController = CylinderController(self.repository.Session)
        cylinderController.copy_all(game.id, gameModel.cylinders)

        return game
    
    def get_allGames(self):
        games = self.repository.find_allGames()
        return [ self.to_json(game) for game in games ]

    def get_game(self, gameId: int):
        game: Game = self.repository.find_gameById(gameId)
        if game is None:
            raise GameNotFoundException(f"Game [{gameId}] not found")
        return game
    
    def delete_game(self, gameId: int):
        game: Game = self.get_game(gameId)

        teamController: TeamController = TeamController(self.repository.Session)
        for team in game.teams:
            if not teamController.isDeletable(team):
                raise ActionNotPermittedException("Game can not be deleted because ")

        for team in game.teams:
            if not teamController.delete(team.id):
                raise ActionNotPermittedException(f"Player [{player.id}] has location history. He can not be deleted")

        cylinderController: CylinderController = CylinderController(self.repository.Session)
        cylinderController.delete_all(game.cylinders)
        return self.repository.delete(game)
    
    def score_game_total(self, gameId: int):
        game: Game = self.get_game(gameId)
        scoring_method = game.scoringType
        scoring_total = self.factory.get_scoring_system(scoring_method).score_igame(game)
        return scoring_total

    def score_game(self, gameId: int):
        game: Game = self.get_game(gameId)
        scoring_method = game.scoringType
        scoring_latest = self.factory.get_scoring_system(scoring_method).score_latest_update(game)
        return scoring_latest
    
    def is_on(self, game: Game):
        return game.startDate < datetime.utcnow() and datetime.utcnow() <= game.endDate

    def is_over(self, game: Game):
        return datetime.utcnow() > game.endDate
    
    def to_json(self, game: Game):
        cylinderController: CylinderController = CylinderController(self.repository.Session)
        json: dict[str, Any] = {
            'id': game.id,
            'name': game.name,
            'scoring_system': game.scoringType,
            'cylinders': [ cylinderController.to_json(cylinder) for cylinder in game.cylinders ]
        }

        if GameType.PLAY.name == game.type:
            if not self.is_on(game):
                status = GameStatus.NOT_SET
            elif self.is_on(game):
                status = GameStatus.RUNNING 
            else:
                status = GameStatus.FINISHED
            
            teamController: TeamController = TeamController(self.repository.Session)
            json.update({
                        'status': status.name,
                        'start_date': game.startDate.timestamp(),
                        'end_date': game.endDate.timestamp(),
                        'teams': [ teamController.to_json(team) for team in game.teams ]
                        })

        return json

# Team
class TeamController:
    def __init__(self, session: Session):
        self.repository: TeamRepository = TeamRepository(session)

    def create(self, name: str, gameId: int):
        return self.repository.create(self.get_name(name), gameId, self.change_color())

    def get(self, teamId: int):
        team = self.repository.find_teamById(teamId)
        if team is None:
            raise TeamNotFoundException(f"Team [{teamId}] not found")
        return team
    
    def update(self, teamId: int, name: str, gameId: int, color: int):
        if name is None and color is None and gameId is None:
            raise TeamAttributMissingException("Team name or color can not be empty")

        team: Team = self.get(teamId)
        
        if name is not None:
            team.name = self.get_name(name)

        if gameId is not None:
            if team.gameId is not None:
                raise ActionNotPermittedException(f"Team [{teamId}] has already a game [{team.gameId}]. Can not change for the new one [{gameId}] ")
            team.gameId = gameId
        
        if color is not None:
            team.color = self.get_color(color)

        return self.repository.update(team)

    def delete(self, teamId: int):
        team: Team = self.get(teamId)
        if self.isDeletable(team):
            return self.repository.delete(team)
        return False
    
    def isDeletable(self, team: Team):
        playerController: PlayerController = PlayerController(self.repository.Session)

        for player in team.players:
            if not playerController.isDeletable(player):
                return False
        return True
    
    def to_json(self, team: Team):
        playerController: PlayerController = PlayerController(self.repository.Session)
        return {
            'id':   team.id,
            'name': team.name,
            'color':  self.get_colorHex(team.color),
            'players': [ playerController.to_json(player) for player in team.players ]
        }

    def get_colorHex(self, color: int):
        return "{0:0{1}x}".format(color, 6)

    def change_color(self):
        return random.randrange(0,16000000)
    
    def get_color(self, color):
        colorValue: int = None
        if isinstance(color, bool) and color == True:
            colorValue = self.change_color()
        elif isinstance(color, int):
            colorValue = int(color)
        else:
            raise TeamColorTypeNotValidException("Color type is not valid")
        return colorValue
    
    def get_name(self, name: str):
        if name is None:
            raise InvalidNameException("Game name does not exist")
        if name.isspace():
            raise InvalidNameException("Game name can not be empty")
        return name


# Player 
class PlayerController:
    def __init__(self, session: Session):
        self.repository: PlayerRepository = PlayerRepository(session)

    def get(self, playerId: int):
        player: Player = self.repository.find_playerById(playerId)
        if player is None:
            raise PlayerNotFoundException(f"Player [{playerId}] not found")
        return player
    
    def create(self, name: str, teamId: int):
        return self.repository.create(name, teamId)
    
    def update(self, playerId: int, name: str, teamId: int):
        player: Player = self.get(playerId)

        if not name.isspace():
            player.name = name

        if teamId is not None:
            teamController: TeamController = TeamController(self.repository.Session)
            team: Team = teamController.get(teamId)
            player.team = team

        return self.repository.update(player)
 
    def update_location(self, playerId: int, latitude: float, longitude: float, altitude: float):
        player: Player = self.get(playerId)
        
        team = player.team
        if team is None:
            raise PlayerLocationException(f"Update location can not be set for the player [{playerId}] because he does not have a team")

        game = team.game
        gameController: GameController = GameController(self.repository.Session)
        if not gameController.is_on(game):
            raise PlayerLocationException(f"Update location can not be set for the player [{playerId}] because the game [{game.id}] is over")

        locationController: LocationHistoryController = LocationHistoryController(self.repository.Session)
        location = locationController.create(player.id, latitude, longitude, altitude)
        player.locationHistory.append(location)
        return self.repository.update(player)

    def isDeletable(self, player: Player):
        if len(player.locationHistory) > 0:
            #abort(400, description=f"Player [{player.id}] has location history. He can not be deleted")
            return False
        return True
    
    def last_position(self, player: Player):
        locationController: LocationHistoryController = LocationHistoryController(self.repository.Session)
        return locationController.to_json(player.locationHistory[-1]) if len(player.locationHistory) > 0 else None
    
    def to_json(self, player: Player):
        return { 
            "id": player.id,
            "name": player.name,
            "last_position": self.last_position(player)
        }
    
    def randomWord(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

# LocationHistory 
class LocationHistoryController:
    def __init__(self, session: Session):
        self.repository: LocationHistoryRepository = LocationHistoryRepository(session)

    def create(self, playerId: int, latitude: float, longitude: float, altitude: float):
        return self.repository.create(playerId, latitude, longitude, altitude)
    
    def to_json(self, location: LocationHistory):
        return {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'altitude': location.altitude,
            'timestamp': location.timestamp.timestamp()
        }

# Cylinder
class CylinderController():
    def __init__(self, session: Session):
        self.repository: CylinderRepository = CylinderRepository(session)

    def create(self, gameId: int, latitude: float, longitude: float, radius: float):
        return self.repository.create(gameId, latitude, longitude, radius)
    
    def copy(self, gameId: int, cylinder: Cylinder):
        return self.create(gameId, cylinder.latitude, cylinder.longitude, cylinder.radius)
    
    def copy_all(self, gameId: int, cylinders: list[Cylinder]):
        new_cylinders: list[Cylinder] = []
        for cylinder in cylinders:
            new_cylinders.append(self.copy(gameId, cylinder))
        return new_cylinders

    def delete(self, cylinder: Cylinder):
        return self.repository.delete(cylinder)

    def delete_all(self, cylinders: list[Cylinder]):
        for cylinder in cylinders:
            if not self.delete(cylinder):
                return False
        return True

    def to_json(self, cylinder: Cylinder):
        return { 
            "id": cylinder.id,
            "latitude": cylinder.latitude,
            "longitude": cylinder.longitude,
            "radius" : cylinder.radius
        }
