import json
from typing import Union

from pydantic import BaseModel


class Base(BaseModel):
    """
    This is Base, here am i
    """

    @classmethod
    def load(cls, data: Union[dict, bytes]) -> object:
        """Loads a dynamic Dictionary or byte string containing dynamic Dictionary.
        Sets the inner key, values into the Pydantic Object

        Args:
            data (Union[dict, bytes]): Can either be a Dictionary or en encoded string of the Dictionary.

        Returns:
            object: Pydantic object that represents the Data.
        """
        if type(data) is dict:
            return cls(**data)
        loaded = json.loads(data.decode())
        return cls(**loaded)

    def dump(self) -> bytes:
        """_summary_

        Returns:
            bytes: _description_
        """
        return self.json().encode()

    def update_fields(self, object: dict):
        """_summary_

        Args:
            object (dict): _description_

        Returns:
            _type_: _description_
        """
        for key, value in object.items():
            if key in self.__fields__:
                setattr(self, key, value)
        return self
