"""Learning unit content modules for MAF Metall/Kunststoff."""

from app.data.content.units.m01 import UNITS as M01_UNITS
from app.data.content.units.m02 import UNITS as M02_UNITS
from app.data.content.units.m03 import UNITS as M03_UNITS
from app.data.content.units.m04 import UNITS as M04_UNITS
from app.data.content.units.m05 import UNITS as M05_UNITS
from app.data.content.units.m06 import UNITS as M06_UNITS
from app.data.content.units.m06_messschieber import UNITS as M06_MESSSCHIEBER_UNITS
from app.data.content.units.m07 import UNITS as M07_UNITS
from app.data.content.units.m08 import UNITS as M08_UNITS
from app.data.content.units.m09 import UNITS as M09_UNITS
from app.data.content.units.m10 import UNITS as M10_UNITS
from app.data.content.units.m11 import UNITS as M11_UNITS
from app.data.content.units.m12 import UNITS as M12_UNITS
from app.data.content.units.m13_m24 import UNITS as M13_M24_UNITS
from app.data.content.units.open_questions import OPEN as ALL_OPEN

ALL_UNITS = [
    *M01_UNITS,
    *M02_UNITS,
    *M03_UNITS,
    *M04_UNITS,
    *M05_UNITS,
    *M06_UNITS,
    *M06_MESSSCHIEBER_UNITS,
    *M07_UNITS,
    *M08_UNITS,
    *M09_UNITS,
    *M10_UNITS,
    *M11_UNITS,
    *M12_UNITS,
    *M13_M24_UNITS,
]

__all__ = ["ALL_UNITS", "ALL_OPEN"]
