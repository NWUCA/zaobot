from pydantic import BaseModel

class FuDu(BaseModel):
    msg: str
    repeat: int = 1
    has_fu_du: bool = False

    def zero(self, msg):
        self.msg = msg
        self.repeat = 1
        self.has_fu_du = False
