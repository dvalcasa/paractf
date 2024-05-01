# game.py
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from models import *
from scoring_models import ScoringType
from datetime import datetime

class Repository:
    db_url='sqlite:///game.db'

    def __init__(self):
        self.engine = create_engine(self.db_url, echo=True)
        Base.metadata.create_all(self.engine)
        self.s = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.s)
        
# Game
class GameRepository():
    def __init__(self, session: Session):
        self.Session = session

    def find_allGameModels(self):
        return self.Session.query(Game).where(Game.type == GameType.MODEL.name).all()
    
    def find_gameModelById(self, gameModelId: int):
        return self.Session.query(Game).where(Game.type == GameType.MODEL.name, Game.id == gameModelId).first()
    
    def find_allGames(self):
        return self.Session.query(Game).where(Game.type == GameType.PLAY.name).all()
 
    def find_gameById(self, gameId: int):
        return self.Session.query(Game).where(Game.type == GameType.PLAY.name, Game.id == gameId).first()
    
    def create(self, name: str, type: GameType, password: str, startDate: datetime, endDate: datetime, scoringType: ScoringType):
        game = Game(name, type.name, password, startDate, endDate, scoringType.name)
        self.Session.add(game)
        self.Session.commit()
        return game
    
    def update(self, game: Game):
        self.Session.add(game)
        self.Session.commit()
        return game
    
    def create_model(self, name: str):
        return self.create(name, GameType.MODEL, None, datetime.utcnow(), datetime.utcnow(), ScoringType.DEGRESS)
    
    def create_game(self, name:str, password: str, startDate: datetime, endDate: datetime, scoringType: ScoringType):
        return self.create(name, GameType.PLAY, password, startDate, endDate, scoringType)
    
    def delete(self, game: Game):
        self.Session.delete(game)
        self.Session.commit()
        return True

# Team
class TeamRepository():
    def __init__(self, session: Session):
        self.Session = session

    def find_teamById(self, teamId: int):
        return self.Session.query(Team).get(teamId)
    
    def create(self, name: str, gameId: int, color: int):
        team = Team(name, gameId, color)
        self.Session.add(team)
        self.Session.commit()
        return team
    
    def update(self, team: Team):
        self.Session.add(team)
        self.Session.commit()
        return team
    
    def delete(self, team: Team):
        self.Session.delete(team)
        self.Session.commit()
        return True

# Player
class PlayerRepository():
    def __init__(self, session: Session):
        self.Session = session

    def find_playerById(self, playerId: int):
        return self.Session.query(Player).get(playerId)
    
    def create(self, name: str, teamId: int):
        player = Player(name, teamId, None)
        self.Session.add(player)
        self.Session.commit()
        return player
    
    def update(self, player: Player):
        self.Session.add(player)
        self.Session.commit()
        return player
    
    def delete(self, player: Player):
        self.Session.delete(player)
        self.Session.commit()
        return True

# LocationHistory
class LocationHistoryRepository():
    def __init__(self, session: Session):
        self.Session = session

    def create(self, playerId: int, latitude: float, longitude: float, altitude: float):
        location = LocationHistory(playerId, latitude, longitude, altitude, timestamp=datetime.utcnow())
        self.Session.add(location)
        self.Session.commit()
        return location

# Cylinder
class CylinderRepository():
    def __init__(self, session: Session):
        self.Session = session

    def create(self, gameId: int, latitude: float, longitude: float, radius: float):
        cylinder = Cylinder(gameId, latitude, longitude, radius)
        self.Session.add(cylinder)
        self.Session.commit()
        return cylinder
    
    def delete(self, cylinder: Cylinder):
        self.Session.delete(cylinder)
        self.Session.commit()
        return True
