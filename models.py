# models.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    #altitude_threshold = Column(Float)
    teams = relationship('Team', back_populates='game')
    cylinders = relationship('Cylinder', back_populates='game')

    def __init__(self, name, cylinders):
        self.name = name
        self.cylinders = cylinders

    def to_json(self):
        return {
            'id': self.id,
            'cylinders': [ c.to_json() for c in self.cylinders ]
        }
    
class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    game_id = Column(Integer, ForeignKey('games.id'))
    game = relationship('Game', back_populates='teams')
    members = relationship('TeamMember', back_populates='team')

class TeamMember(Base):
    __tablename__ = 'teammembers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    team_id = Column(Integer, ForeignKey('teams.id'))
    team = relationship('Team', back_populates='members')
    location_history = relationship('LocationHistory', back_populates='member')

class LocationHistory(Base):
    __tablename__ = 'locationhistory'
    id = Column(Integer, primary_key=True)
    team_member_id = Column(Integer, ForeignKey('teammembers.id'))
    member = relationship('TeamMember', back_populates='location_history')
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Cylinder(Base):
    __tablename__ = 'cylinders'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    game = relationship('Game', back_populates='cylinders')
    latitude = Column(Float)
    longitude = Column(Float)
    radius = Column(Float)

    def __init__(self, latitude, longitude, radius):
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius

    def to_json(self):
        return { "id": self.id,
                 "game": self.game_id,
                 "latitude": self.latitude,
                 "longitude": self.longitude,
                 "radius" : self.radius
                 }
