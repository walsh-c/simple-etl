import datetime
from pydantic import BaseModel, ValidationError


class AISSchema(BaseModel):
    """Data class for the expected schema for the Denmark AIS data.
    """
    timestamp: datetime.datetime
    type_of_mobile: str
    mmsi: int
    latitude: float
    longitude: float
    navigational_status: str
    rot: float
    sog: float
    cog: float
    heading: float
    imo: str
    callsign: str
    name: str
    ship_type: str
    cargo_type: str
    width: float
    length: float
    type_of_position_fixing_device: str
    draught: float
    destination: str
    eta: datetime.datetime
    data_source_type: str
    a: float
    b: float
    c: float
    d: float


def validate(series, model):
    """Vaildator function that is applied to a single row in a pandas
    dataframe. Expects a row (pd.Series) and a data model such as the AISSchema
    and returns a boolean depending on if the data in the row is valid.
    """
    data = series.to_dict()
    try:
        model(**data)
        return True
    except ValidationError:
        return False
