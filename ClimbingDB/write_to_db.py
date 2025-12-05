from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, Climber, Route, ClimberRoute
from datetime import datetime
from faker import Faker
fake = Faker()
import random

engine = create_engine("sqlite:///climbing.db")
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

def add_climber(sess):
    first = input("First name: ").strip()
    last = input("Last name: ").strip()
    c = Climber(first_name=first, last_name=last)
    sess.add(c)
    sess.commit()
    print(f"Added climber {c.id}: {c.first_name} {c.last_name}")

def add_route(sess):
    name = input("Route name: ").strip()
    grade = input("Route grade: ").strip()
    description = input("Route description: ").strip()
    r = Route(name=name, grade=grade, description=description)
    sess.add(r)
    sess.commit()
    print(f"Added route {r.id}: {r.name}")

def link_climber_route(sess, climber_id, route_id, date_climbed=None):
    climber_id = int(input("Climber ID: ").strip())
    route_id = int(input("Route ID: ").strip())
    date_climbed = input("Date climbed: ").strip()
    if date_climbed is None:
        dt = datetime.now()
        date_climbed = dt.date()
    cr = ClimberRoute(climber_id=climber_id, route_id=route_id, date_climbed=date_climbed)
    sess.add(cr)
    sess.commit()
    print(f"Linked climber {climber_id} to route {route_id}")


with Session(engine) as session: c1 = Climber(first_name="Alex", last_name="Honnold")
c2 = Climber(first_name="Mangus", last_name="Mitbo")
r1 = Route(name="El Capitan", grade="5.13a", description="Endurance Route")
r2 = Route(name="The Nose", grade="5.14a", description="Crack Climbing")
r3 = Route(name="Moonlight Buttress", grade="5.14a", description="Sandstone")
session.add_all([c1, c2, r1, r2, r3])
session.flush()

for i in range(10):
    climber = Climber(first_name=fake.first_name(), last_name=fake.last_name())
    r = Route(name=fake.first_name(), grade="V"+str(random.randint(0,9)), description=fake.first_name())
    session.add(climber)
    session.add(r)

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
        link_climber_route(session, r1.id, r2.id)
    elif choice == "4":
        break
    else:
        print("Invalid choice")