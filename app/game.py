# game.py
from flask import abort
from repository import Repository
from controller import GameController, TeamController, PlayerController, CylinderController, Game, Team
from exception import *

class GameManager:
    repository: Repository = Repository()

    gameController: GameController = GameController(repository.Session)
    teamController: TeamController = TeamController(repository.Session)
    playerController: PlayerController = PlayerController(repository.Session)

    def get_gameModel(self, gameModelId: int):
        try:
            gameModel = self.gameController.get_gameModel(gameModelId)
            return self.gameController.to_json(gameModel)
        except GameModelNotFoundException as ex:
            abort(404, ex)

    def create_model(self, name: str, cylinders: list):
        if name is None:
            abort(400, "Game model name does not exist")

        if name.isspace():
            abort(400, "Game model name can not be empty")

        if cylinders is None:
            abort(400, "Game model cylinders does not exist")

        if not isinstance(cylinders, list):
            abort(400, "Cylinders should be a list")
        if not cylinders:
            abort(400, 'Cylinders list can not be empty')
        
        for cylinder in cylinders:
            if cylinder['longitude'] is None:
                abort(400, 'Cylinder should have a longitude element')
            elif not isinstance(cylinder['longitude'], (float, int)):
                abort(400, 'Cylinder should have a longitude element with float type')
            if cylinder['latitude'] is None:
                abort(400, 'Cylinder should have a latitude element')
            elif not isinstance(cylinder['latitude'], (float, int)):
                abort(400, 'Cylinder should have a latitude element with float type')
            if cylinder['radius'] is None:
                abort(400, 'Cylinder should have a radius element')
            elif not isinstance(cylinder['radius'], (float, int)):
                abort(400, 'Cylinder should have a radius element with float type')
            
        return self.gameController.to_json(self.gameController.create_gameModel(name, cylinders))
    
    def update_model(self, gameModelId: int, name: str, cylinders: list, scoringType: str):
        if name is not None and name.isspace():
            abort(400, 'Game model name can not be empty')

        if cylinders is not None:
            if not isinstance(cylinders, list):
                abort(400, 'Cylinders should be a list')
            if not cylinders:
                abort(400, 'Cylinders list can not be empty')
            
            for cylinder in cylinders:
                if cylinder['longitude'] is None:
                    abort(400, 'Cylinder should have a longitude element')
                elif not isinstance(cylinder['longitude'], (float, int)):
                    abort(400, 'Cylinder should have a longitude element with float type')
                if cylinder['latitude'] is None:
                    abort(400, 'Cylinder should have a latitude element')
                elif not isinstance(cylinder['latitude'], (float, int)):
                    abort(400, 'Cylinder should have a latitude element with float type')
                if cylinder['radius'] is None:
                    abort(400, 'Cylinder should have a radius element')
                elif not isinstance(cylinder['radius'], (float, int)):
                    abort(400, 'Cylinder should have a radius element with float type')

        if name is None and cylinders is None:
            abort(400, 'Game name or cylinders must be given')
        
        try:
            gameModel: Game = self.gameController.update_gameModel(gameModelId, name, cylinders, scoringType)
            return self.gameController.to_json(gameModel)
        except GameModelNotFoundException as ex:
            abort(404, ex)
        except ScoringTypeNotExistingException as ex:
            abort(400, ex)
    
    def delete_gameModel(self, gameModelId: int):
        try:
            isDeleted = self.gameController.delete_model(gameModelId)
            if isDeleted:
                return ""
            else:
                abort(500, "Unexcepted error when deleting game model")
        except GameModelNotFoundException as ex:
            abort(404, ex)
    
    def get_game(self, gameId: int):
        try:
            game = self.gameController.get_game(gameId)
            return self.gameController.to_json(game)
        except GameNotFoundException as ex:
            abort(404, ex)
    
    def create_game(self, gameModelId: int, name: str):
        if name is None:
            abort(400, 'Game name does not exist')

        if name.isspace():
            abort(400, 'Game name can not be empty')
        
        try:
            return self.gameController.to_json(self.gameController.create_game(gameModelId, name, None, None, None))
        except GameModelNotFoundException as ex:
            abort(404, ex)
    
    def delete_game(self, gameId: int):
        try:
            isDeleted = self.gameController.delete_game(gameId)
            if isDeleted:
                return ""
            else:
                abort(500, "Unexcepted error")
        except GameNotFoundException as ex:
            abort(400, ex)
    
    def create_team(self, name: str, gameId: int):
        if gameId is not None:
            try:
                self.gameController.get_game(gameId)
            except GameNotFoundException as ex:
                abort(404, ex)

        try:
            return self.teamController.to_json(self.teamController.create(name, gameId))
        except TeamColorTypeNotValidException as ex:
            abort(400, ex)
        except InvalidNameException as ex:
            abort(400, ex)

    def udpate_team(self, teamId: int, name: str, gameId: int, color):
        if gameId is not None:
            try:
                self.gameController.get_game(gameId)
            except GameNotFoundException as ex:
                abort(404, ex)
        
        try:
            return self.teamController.to_json(self.teamController.update(teamId, name, gameId, color))
        except TeamNotFoundException as ex:
            abort(404, ex)
        except TeamAttributMissingException as ex:
            abort(400, ex)
        except InvalidNameException as ex:
            abort(400, ex)
        except TeamColorTypeNotValidException as ex:
            abort(400, ex)
        except ActionNotPermittedException as ex:
            abort(400, ex)
    
    def delete_team(self, teamId: int):
        try:
            isDeleted = self.teamController.delete(teamId)
            if isDeleted:
                return ""
            else:
                abort(500, "Unexcepted error")
        except TeamNotFoundException as ex:
            abort(404, ex)
    
    def create_player(self, name: str, teamId: int):
        if name is None:
            abort(400, 'Player name does not exist')

        if name.isspace():
            abort(400, 'Player name can not be empty')

        if teamId is not None:
            try:
                self.teamController.get(teamId)
            except TeamNotFoundException as ex:
                abort(400, ex)
        
        return self.playerController.to_json(self.playerController.create(name, teamId))
    
    def update_player(self, playerId: int, name: str, teamId: int):
        if name is not None and name.isspace():
            abort(400, 'Player name can not be empty')

        try:
            player = self.playerController.update(playerId, name, teamId)
            return self.playerController.to_json(player)
        except PlayerNotFoundException as ex:
            abort(404, ex)
        except TeamNotFoundException as ex:
            abort(400, ex)
    
    def update_player_location(self, playerId: int, latitude, longitude, altitude):
        if longitude is None:
            abort(400, 'Location should have a longitude element')
        
        if not isinstance(longitude, (float, int)):
            abort(400, 'Cylinder should have a longitude element with float type')
        
        if latitude is None:
            abort(400, 'Location should have a latitude element')
        
        if not isinstance(latitude, (float, int)):
            abort(400, 'Cylinder should have a latitude element with float type')

        if altitude is None:
            abort(400, 'Location should have a altitude element')
        
        if not isinstance(altitude, (float, int)):
            abort(400, 'Cylinder should have a altitude element with float type')

        try:
            player = self.playerController.update_location(playerId, latitude, longitude, altitude)
            return self.playerController.to_json(player)
        except PlayerNotFoundException as ex:
            abort(404, ex)
        except PlayerLocationException as ex:
            abort(400, ex)
