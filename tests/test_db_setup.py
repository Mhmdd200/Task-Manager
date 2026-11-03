from sqlalchemy import select, text

from app.models import ProjectMember, User


def test_foreign_keys_are_on(db):
    assert db.execute(text("PRAGMA foreign_keys")).scalar() == 1


def test_each_test_starts_with_empty_tables(db):
    assert db.scalars(select(User)).all() == []


def test_factories_create_project_with_owner_membership(make_user, make_project, db):
    owner = make_user("owner")

    project = make_project(owner)

    member = db.scalar(select(ProjectMember).where(ProjectMember.project_id == project.id))
    assert member.user_id == owner.id
    assert member.role == "owner"


def test_auth_headers_authenticate_the_user(client, make_user, auth_headers):
    user = make_user("me")

    response = client.get("/auth/me", headers=auth_headers(user))

    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"
