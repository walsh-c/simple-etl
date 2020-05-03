"""TODO: Implament BaseLoader as a true abstract base class"""

import pandas as pd


class BaseLoader:
    """Base class that all Loaders should inherit from.
    All loaders should implament the .load method which should return a
    pd.DataFrame object.
    """
    def load() -> pd.DataFrame:
        pass


class LocalLoader(BaseLoader):
    """Loader for accessing locally stored csv files"""

    target = "local"

    @staticmethod
    def load(path):
        return pd.read_csv(path)


def get_csv(path, loader="local"):
    loader_class = _get_loader(loader)
    return loader_class.load(path)


def _get_loader(loader):
    sub_classes = BaseLoader.__subclasses__()
    valid_loaders = [i.target for i in sub_classes]
    if loader in valid_loaders:
        return sub_classes[valid_loaders.index(loader)]
    else:
        raise UnknownLoaderError(f"Unknwon loader defined. Acceptable values "
                                 "for location are: {valid_loaders}")


class UnknownLoaderError(Exception):
    pass
