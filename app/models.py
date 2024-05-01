# models.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Optional
from enum import Enum

Base = declarative_base()

class GameType(Enum):
    MODEL = "model",
    PLAY = "play"

class GameStatus(Enum):
    NOT_SET = "not set",
    RUNNING = "running",
    FINISHED = "finished"

class Game(Base):
    __tablename__ = 'game'
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String)
    type: Mapped[str] = Column(String)
    startDate = Column(DateTime(timezone=False))
    endDate = Column(DateTime(timezone=False))
    scoringType: Mapped[str] = Column(String)
    password: Mapped[Optional[str]] = Column(String)
    teams: Mapped[List["Team"]] = relationship(back_populates='game')
    cylinders: Mapped[List["Cylinder"]] = relationship(back_populates='game')

    def __init__(self, name: str, type: str, password: str, startDate: DateTime, endDate: DateTime, scoringType: str):
        self.name = name
        self.type = type
        self.password = password
        self.startDate = startDate
        self.endDate = endDate
        self.scoringType = scoringType
    
class Team(Base):
    __tablename__ = 'team'
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String)
    color: Mapped[int] = Column(Integer)
    gameId: Mapped[int] = Column(Integer, ForeignKey('game.id'))
    password: Mapped[Optional[str]] = Column(String)
    game: Mapped["Game"] = relationship(back_populates='teams')
    players: Mapped[List["Player"]] = relationship(back_populates='team')

    def __init__(self, name: str, gameId: int, color: int):
        self.name = name
        self.gameId = gameId
        self.color = color
 
class Player(Base):
    __tablename__ = 'player'
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String)
    teamId: Mapped[int] = Column(Integer, ForeignKey('team.id'))
    team: Mapped["Team"] = relationship(back_populates='players')
    locationHistory: Mapped[List["LocationHistory"]] = relationship(back_populates='player')

    def __init__(self, name: str, teamId: int, password: str):
        self.name = name
        self.teamId = teamId
        self.password = password

class LocationHistory(Base):
    __tablename__ = 'location_history'
    id: Mapped[int] = Column(Integer, primary_key=True)
    playerId: Mapped[int] = Column(Integer, ForeignKey('player.id'))
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    timestamp = Column(DateTime(timezone=False))
    player: Mapped["Player"] = relationship(back_populates="locationHistory")

    def __init__(self, playerId, latitude, longitude, altitude, timestamp):
        self.playerId = playerId
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.timestamp = timestamp

class Cylinder(Base):
    __tablename__ = 'cylinder'
    id: Mapped[int] = Column(Integer, primary_key=True)
    gameId: Mapped[int] = Column(Integer, ForeignKey('game.id'))
    latitude = Column(Float)
    longitude = Column(Float)
    radius = Column(Float)
    game: Mapped["Game"] = relationship(back_populates='cylinders')

    def __init__(self, gameId: int, latitude: float, longitude: float, radius: float):
        self.gameId = gameId
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius
