from typing import Optional, List
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, DateTime
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class ClimberRoute(Base):
    __tablename__ = "climber_route"

    climber_id: Mapped[int] = mapped_column(ForeignKey("climbers.id"), primary_key=True)
    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id"), primary_key=True
    )
    date_climbed: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # association between ClimberRoute -> Climber
    climber: Mapped["Climber"] = relationship(back_populates="route_associations")

    # association between ClimberRoute -> Route
    route: Mapped["Route"] = relationship(back_populates="climber_associations")


class Climber(Base):
    __tablename__ = "climbers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    last_name: Mapped[str]
    first_name: Mapped[str]

    # many-to-many relationship to Routes, bypassing the ClimberRoutes class
    routes_climbed: Mapped[List["Route"]] = relationship(
        secondary="climber_route",
        back_populates="climbed_by",
        # overlaps="climber, route",
        # viewonly=True,
    )

    # association between Climber -> ClimberRoutes -> Routes
    route_associations: Mapped[List["ClimberRoute"]] = relationship(
        back_populates="climber",
        # overlaps="routes_climbed"
    )


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]

    # many-to-many relationship to Parent, bypassing the `Association` class
    climbed_by: Mapped[List["Climber"]] = relationship(
        secondary="climber_route",
        back_populates="routes_climbed",
        # overlaps="climber, route",
        # viewonly=True,
    )

    # association between Route -> ClimberRoute -> Climber
    climber_associations: Mapped[List["ClimberRoute"]] = relationship(
        back_populates="route",
        # overlaps="route_associations"
    )