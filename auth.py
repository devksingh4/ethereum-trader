import json as jlib
class Credentials:
  def __init__(self, filename: str):
    f = open(filename, 'r')
    json = jlib.load(f)
    f.close()
    self.key: str = json['key']
    self.b64secret: str = json['b64secret']
    self.passphrase: str = json['passphrase']

  def getCreds(self) -> dict:
    return self.key, self.b64secret, self.passphrase