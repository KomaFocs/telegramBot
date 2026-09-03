from enum import Enum

class FA_Type(Enum):
	ARTE = "art"
	MUSICA = "music"
	STORIA = "story"
	POESIA = "poetry"
	FLASH = "flash"

	@classmethod
	def from_str(cls, label:str) -> str:
		if not label:
			return cls.ARTE.value
		try:
			return cls[label.upper()].value
		except KeyError:
			return cls.ARTE.value
