from dataclasses import dataclass


@dataclass
class User:
	name:str
	link:str

	def __init__(self, name:str, link:str):
		self.name = name
		self.link = link
