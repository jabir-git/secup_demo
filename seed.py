"""Seed script to populate database with fake data for testing."""

import random
from faker import Faker
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database import create_db_tables, get_session
from app.models import User, Vehicle

fake = Faker(["fr_FR", "en_US"])  # French and English data
Faker.seed(42)  # For reproducible data

# Stable credentials for mobile app integration testing.
MOBILE_TEST_USERS: dict[str, dict[str, str]] = {
    "agent_alpha": {
        "username": "agent.alpha",
        "email": "agent.alpha@secup.gn",
        "password": "AgentAlpha@2026!",
    },
    "agent_bravo": {
        "username": "agent.bravo",
        "email": "agent.bravo@secup.gn",
        "password": "AgentBravo@2026!",
    },
    "supervisor_charlie": {
        "username": "supervisor.charlie",
        "email": "supervisor.charlie@secup.gn",
        "password": "SupervisorCharlie@2026!",
    },
}


def clear_database(session: Session) -> None:
    """Clear all data from tables."""
    print("Clearing existing data...")
    session.query(Vehicle).delete()
    session.query(User).delete()
    session.commit()
    print("✓ Database cleared")


def _create_fixed_mobile_users(session: Session) -> list[User]:
    users: list[User] = []
    for payload in MOBILE_TEST_USERS.values():
        user = User(
            username=payload["username"],
            email=payload["email"],
            hashed_password=hash_password(payload["password"]),
        )
        session.add(user)
        users.append(user)
    return users


def seed_users(session: Session, count: int = 10) -> list[User]:
    """Create fake users (police officers)."""
    print(f"\nCreating {count} users...")
    users: list[User] = _create_fixed_mobile_users(session)

    extra_count = max(0, count - len(users))
    for i in range(extra_count):
        user = User(
            username=f"officer{1000 + i}",
            email=f"officer{1000 + i}@secup.gn",
            hashed_password=hash_password("password123"),
        )
        session.add(user)
        users.append(user)

    session.commit()
    print(f"✓ Created {len(users)} users")
    return users


def seed_vehicles(session: Session, count: int = 80) -> list[Vehicle]:
    """Create fake vehicles with embedded driver info."""
    print(f"\nCreating {count} vehicles...")
    vehicles: list[Vehicle] = []

    vehicle_makes = [
        "Peugeot", "Renault", "Citroën", "Toyota", "Mercedes-Benz",
        "BMW", "Volkswagen", "Ford", "Nissan", "Hyundai", "Kia",
    ]
    vehicle_types = [
        "Berline", "SUV", "Citadine", "Break", "Camionnette",
        "Moto", "4x4", "Coupé", "Monospace",
    ]
    colors = [
        "Noir", "Blanc", "Gris", "Bleu", "Rouge",
        "Argent", "Vert", "Marron", "Jaune",
    ]

    used_license_numbers: set[str] = set()

    for _ in range(count):
        plate_prefix = random.choice(["GY", "CN", "KB", "KA", "LA", "MM", "NZ"])
        plate_number = fake.random_int(1000, 9999)
        plate_suffix = (
            f"{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}"
        )
        license_plate = f"{plate_prefix}-{plate_number}-{plate_suffix}"

        make = random.choice(vehicle_makes)
        vehicle_type = random.choice(vehicle_types)
        color = random.choice(colors)
        year = fake.random_int(2000, 2026)
        vehicle_info = f"{make} - {vehicle_type} - {year} - {color}"

        while True:
            candidate = (
                f"{fake.random_int(10000000, 99999999)}{fake.random_int(1000, 9999)}"
            )
            if candidate not in used_license_numbers:
                used_license_numbers.add(candidate)
                license_number = candidate
                break

        vehicle = Vehicle(
            license_plate=license_plate,
            vehicle_info=vehicle_info,
            notes=fake.sentence(),
            status=random.choices(
                ["normal", "wanted", "stolen", "suspicious"],
                weights=[80, 10, 5, 5],
            )[0],
            event_type=random.choices(
                ["alert", "intervention", None],
                weights=[20, 20, 60],
            )[0],
            driver_full_name=fake.name(),
            driver_license_number=license_number,
            driver_phone=fake.phone_number(),
        )
        session.add(vehicle)
        vehicles.append(vehicle)

    session.commit()
    print(f"✓ Created {len(vehicles)} vehicles")
    return vehicles


def seed_database(
    reset: bool = True,
    if_empty_only: bool = False,
    users_count: int = 10,
    vehicles_count: int = 80,
) -> None:
    """Seed database with realistic non-null demo data."""
    create_db_tables()

    with next(get_session()) as session:
        if if_empty_only:
            has_users = session.execute(select(User.id).limit(1)).first() is not None
            if has_users:
                return

        if reset:
            clear_database(session)

        users = seed_users(session, count=users_count)
        vehicles = seed_vehicles(session, count=vehicles_count)

        print("\n" + "=" * 60)
        print("SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  • {len(users)} users created")
        print(f"  • {len(vehicles)} vehicles created")
        print(f"\nTotal records: {len(users) + len(vehicles)}")
        print("\nTest user dictionary for mobile app:")
        for key, payload in MOBILE_TEST_USERS.items():
            print(
                f"  {key}: username={payload['username']} | password={payload['password']}"
            )
        print("=" * 60)


def main() -> None:
    """Main seeding function."""
    print("=" * 60)
    print("DATABASE SEEDING SCRIPT")
    print("=" * 60)
    seed_database(reset=True, if_empty_only=False)


if __name__ == "__main__":
    main()
