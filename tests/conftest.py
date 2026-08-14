import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import RecipientProfile


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
def isolated_database():
    Base.metadata.create_all(bind=test_engine)

    with TestSessionLocal() as db:
        db.add_all(
            [
                RecipientProfile(
                    email="tanaka@abc.jp",
                    name="Tanaka",
                    country_code="JP",
                    language_code="ja",
                    relationship_type="PARTNER",
                    organization="ABC Design",
                ),
                RecipientProfile(
                    email="alex@example.com",
                    name="Alex",
                    country_code="US",
                    language_code="en",
                    relationship_type="CLIENT",
                    organization="Example Inc.",
                ),
            ]
        )
        db.commit()

    def override_get_db():
        with TestSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
