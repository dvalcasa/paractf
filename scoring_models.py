from math import radians, sin, cos, sqrt, atan2

# Abstract super class
class Scoring():
    def __init__(self):
        return

    def haversine(self, lat1, lon1, lat2, lon2):
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = 6371000 * c  # Radius of the Earth in meters

        return distance

    def is_coordinate_within_circle(self, coord, center, radius):
        # coord and center should be tuples (latitude, longitude)
        distance = self.haversine(coord[0], coord[1], center[0], center[1])
        return distance <= radius

    def score_igame(self, igame):
        return False

    def score_latest_update(self, igame):
        return []

class ScoringTraditional(Scoring):
    def __init__(self):
        super().__init__()

    def score_igame(self, igame):
        return {}

    def score_latest_update(self, igame):
        #igame = self.Session.query(GameInstance).get(igame_id)
        validations = []
        for c in igame.game.cylinders:
            valid = {
                "cylinder_id": c.id,
                "lat": c.latitude,
                "lon": c.longitude,
                "radius": c.radius,
                "valid_time": 0,
                "valid_color": None,
                "valid_team": None
            }
            validations.append(valid)
        histories = []
        
        for t in igame.teams:
            print (t.name)
            for m in t.members:
                for lh in m.location_history:
                    for v in validations:
                        if self.is_coordinate_within_circle((lh.latitude, lh.longitude),(v['lat'], v['lon']),v['radius']) and v['valid_time'] < int(lh.timestamp.timestamp()):
                            v['valid_time'] = lh.timestamp.timestamp()
                            v['valid_team'] = t.id
                            v['valid_color'] = t.get_color_hex()
        return (validations)


class ScoringFactory():
    def __init__(self):
        return
    
    def get_scoring_system(self, system):
        match system:
            case 'trad':
                return ScoringTraditional()

        return ScoringTraditional()
        
