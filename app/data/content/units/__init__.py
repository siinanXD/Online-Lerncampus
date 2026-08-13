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
from app.data.content.units.m13 import UNITS as M13_UNITS
from app.data.content.units.m14 import UNITS as M14_UNITS
from app.data.content.units.m15 import UNITS as M15_UNITS
from app.data.content.units.m16 import UNITS as M16_UNITS
from app.data.content.units.m17 import UNITS as M17_UNITS
from app.data.content.units.m18 import UNITS as M18_UNITS
from app.data.content.units.m19 import UNITS as M19_UNITS
from app.data.content.units.m20 import UNITS as M20_UNITS
from app.data.content.units.m21 import UNITS as M21_UNITS
from app.data.content.units.m22 import UNITS as M22_UNITS
from app.data.content.units.m23 import UNITS as M23_UNITS
from app.data.content.units.m24 import UNITS as M24_UNITS
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
    *M13_UNITS,
    *M14_UNITS,
    *M15_UNITS,
    *M16_UNITS,
    *M17_UNITS,
    *M18_UNITS,
    *M19_UNITS,
    *M20_UNITS,
    *M21_UNITS,
    *M22_UNITS,
    *M23_UNITS,
    *M24_UNITS,
]

__all__ = ["ALL_UNITS", "ALL_OPEN"]
