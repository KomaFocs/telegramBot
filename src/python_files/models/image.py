from dataclasses import dataclass, field

@dataclass
class Image:
	author:str=""
	_tags:list[str] = field(default_factory=list)
	submission_link:str=""
	preview_link:str=""
	submission_id:int=0


	@property
	def tags(self) -> list[str]:
		return self._tags


	def get_tags(self, count:int=0) -> list[str]:
		return self._tags if count <= 0 else self._tags[:count]


	def clean_tags(self) -> list[str]:
		taglist = []
		for tag in self._tags:
			if not (len(tag) >= 2 and tag[0].isalpha() and tag[1] == "_"):
				# ignora i tag singolo carattere seguiti da un underscore (i.e.: u_username)
				clean_tag = tag.replace("-", "_")  # clear-sky -> clear_sky
				taglist.append(f"#{clean_tag}")
		return taglist


	def format_description(self) -> str:
		return f"Utente: {self.author}\nTag: {', '.join(self.clean_tags())}\nLink: {self.submission_link}"

