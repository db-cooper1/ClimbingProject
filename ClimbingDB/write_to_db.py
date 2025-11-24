from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, Climber, Route, ClimberRoute
from datetime import datetime

engine = create_engine("sqlite:///climbing.db")
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

def add_climber(session):
    first = input("First name: ").strip()
    last = input("Last name: ").strip()
    c = Climber(first_name=first, last_name=last)
    session.add(c)
    session.commit()
    print(f"Added climber {c.id}: {c.first_name} {c.last_name}")

def add_route(session):
    name = input("Route name: ").strip()
    grade = input("Route grade: ").strip()
    description = input("Route description: ").strip()
    r = Route(name=name)
    q = Route(grade=grade)
    t = Route(description=description)
    session.add(r, q, t)
    session.commit()
    print(f"Added route {r.id}: {r.name}")

def link_climber_route(session, climber_id, route_id, date_climbed=None):
    # climber_id = int(input("Climber ID: ").strip())
    # route_id = int(input("Route ID: ").strip())
    # date_climbed = input("Date climbed: ").strip()
    if date_climbed is None:
        date_climbed = (datetime.utcnow).split(" ")[0]
    cr = ClimberRoute(
        climber_id=climber_id,
        route_id=route_id,
        date_climbed=date_climbed,
    )
    session.add(cr)
    session.commit()
    print(f"Linked climber {climber_id} to route {route_id}")


with Session(engine) as session: c1 = Climber(first_name="Alex", last_name="Honnold")
c2 = Climber(first_name="Mangus", last_name="Mitbo")
r1 = Route(name="El Capitan", grade="5.13a", description="Endurance Route")
r2 = Route(name="The Nose", grade="5.14a", description="Crack Climbing")
r3 = Route(name="Moonlight Buttress", grade="5.14a", description="Sandstone")
session.add_all([c1, c2, r1, r2, r3])
session.flush()


session.add_all([ClimberRoute(climber_id=c1.id, route_id=r1.id),
                 ClimberRoute(climber_id=c1.id, route_id=r2.id),
                 ClimberRoute(climber_id=c2.id, route_id=r2.id),
                 ClimberRoute(climber_id=c2.id, route_id=r3.id), ])
session.commit()
while True:
    print("\n1 = Add Climber")
    print("2 = Add Route")
    print("3 = Add Climb")
    print("4 = Quit")
    choice = input("Choose: ").strip()

    if choice == "1":
        add_climber(session)
    elif choice == "2":
        add_route(session)
    elif choice == "3":
        link_climber_route(session)
    elif choice == "4":
        break
    else:
        print("Invalid choice")