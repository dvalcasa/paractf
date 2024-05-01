
class InvalidNameException(Exception):
    def __init__(self, technicalMessage: str):
        super().__init__(f"Invalid name: {technicalMessage}")

class GameModelNotFoundException(Exception):
    pass

class GameNotFoundException(Exception):
    pass

class TeamNotFoundException(Exception):
    pass 

class TeamAttributMissingException(Exception):
    pass

class TeamColorTypeNotValidException(Exception):
    pass

class PlayerNotFoundException(Exception):
    pass

class PlayerLocationException(Exception):
    pass

class ScoringTypeNotExistingException(Exception):
    pass

class ActionNotPermittedException(Exception):
    pass