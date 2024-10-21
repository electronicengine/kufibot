import py_qmc5883l

class CompassDriver:
    _instance = None  

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'sensor'):
            self.sensor = py_qmc5883l.QMC5883L()

    def get_angle(self):
        return self.sensor.get_bearing()

    def get_magnet(self):
        return self.sensor.get_magnet()
    
    def get_all(self):
        return {"angle": self.get_angle(), "magnet": self.get_magnet()}
        
