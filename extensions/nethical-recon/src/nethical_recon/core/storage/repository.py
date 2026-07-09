"""Repository pattern for data access."""

from __future__ import annotations

import ast
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from ..models import IOC, APIKey, Asset, Evidence, Finding, ScanJob, Target, ToolRun, User
from .models import (
    APIKeyModel,
    AssetModel,
    EvidenceModel,
    FindingModel,
    IOCModel,
    ScanJobModel,
    TargetModel,
    ToolRunModel,
    UserModel,
)

DomainModel = TypeVar("DomainModel")
ORMModel = TypeVar("ORMModel")


class BaseRepository(Generic[DomainModel, ORMModel]):
    """Base repository for CRUD operations."""

    def __init__(self, session: Session, orm_model: type[ORMModel], domain_model: type[DomainModel]):
        """Initialize repository.

        Args:
            session: SQLAlchemy session.
            orm_model: ORM model class.
            domain_model: Domain model class.
        """
        self.session = session
        self.orm_model = orm_model
        self.domain_model = domain_model

    def create(self, entity: DomainModel) -> DomainModel:
        """Create a new entity.

        Args:
            entity: Domain model instance.

        Returns:
            Created entity.
        """
        orm_instance = self.orm_model(**entity.model_dump())
        self.session.add(orm_instance)
        self.session.flush()
        return self._to_domain(orm_instance)

    def get_by_id(self, entity_id: UUID) -> DomainModel | None:
        """Get entity by ID.

        Args:
            entity_id: Entity ID.

        Returns:
            Domain model instance or None.
        """
        orm_instance = self.session.query(self.orm_model).filter(self.orm_model.id == entity_id).first()
        return self._to_domain(orm_instance) if orm_instance else None

    def get_all(self, limit: int | None = None, offset: int = 0) -> list[DomainModel]:
        """Get all entities.

        Args:
            limit: Maximum number of entities to return.
            offset: Number of entities to skip.

        Returns:
            List of domain model instances.
        """
        query = self.session.query(self.orm_model)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return [self._to_domain(orm_instance) for orm_instance in query.all()]

    def update(self, entity_id: UUID, updates: dict) -> DomainModel | None:
        """Update entity.

        Args:
            entity_id: Entity ID.
            updates: Fields to update.

        Returns:
            Updated domain model instance or None.
        """
        orm_instance = self.session.query(self.orm_model).filter(self.orm_model.id == entity_id).first()
        if not orm_instance:
            return None

        for key, value in updates.items():
            if hasattr(orm_instance, key):
                setattr(orm_instance, key, value)

        self.session.flush()
        return self._to_domain(orm_instance)

    def delete(self, entity_id: UUID) -> bool:
        """Delete entity.

        Args:
            entity_id: Entity ID.

        Returns:
            True if deleted, False otherwise.
        """
        result = self.session.query(self.orm_model).filter(self.orm_model.id == entity_id).delete()
        return result > 0

    def _to_domain(self, orm_instance: ORMModel) -> DomainModel:
        """Convert ORM model to domain model.

        Args:
            orm_instance: ORM model instance.

        Returns:
            Domain model instance.
        """
        data = {c.name: getattr(orm_instance, c.name) for c in orm_instance.__table__.columns}
        return self.domain_model(**data)


class TargetRepository(BaseRepository[Target, TargetModel]):
    """Repository for Target entities."""

    def __init__(self, session: Session):
        super().__init__(session, TargetModel, Target)

    def get_by_value(self, value: str) -> Target | None:
        """Get target by value.

        Args:
            value: Target value.

        Returns:
            Target or None.
        """
        orm_instance = self.session.query(self.orm_model).filter(self.orm_model.value == value).first()
        return self._to_domain(orm_instance) if orm_instance else None


class ScanJobRepository(BaseRepository[ScanJob, ScanJobModel]):
    """Repository for ScanJob entities."""

    def __init__(self, session: Session):
        super().__init__(session, ScanJobModel, ScanJob)

    def get_by_target(self, target_id: UUID) -> list[ScanJob]:
        """Get jobs by target ID.

        Args:
            target_id: Target ID.

        Returns:
            List of scan jobs.
        """
        orm_instances = self.session.query(self.orm_model).filter(self.orm_model.target_id == target_id).all()
        return [self._to_domain(orm_instance) for orm_instance in orm_instances]


class ToolRunRepository(BaseRepository[ToolRun, ToolRunModel]):
    """Repository for ToolRun entities."""

    def __init__(self, session: Session):
        super().__init__(session, ToolRunModel, ToolRun)

    def get_by_job(self, job_id: UUID) -> list[ToolRun]:
        """Get tool runs by job ID.

        Args:
            job_id: Job ID.

        Returns:
            List of tool runs.
        """
        orm_instances = self.session.query(self.orm_model).filter(self.orm_model.job_id == job_id).all()
        return [self._to_domain(orm_instance) for orm_instance in orm_instances]


class EvidenceRepository(BaseRepository[Evidence, EvidenceModel]):
    """Repository for Evidence entities."""

    def __init__(self, session: Session):
        super().__init__(session, EvidenceModel, Evidence)

    def get_by_run(self, run_id: UUID) -> list[Evidence]:
        """Get evidence by run ID.

        Args:
            run_id: Run ID.

        Returns:
            List of evidence.
        """
        orm_instances = self.session.query(self.orm_model).filter(self.orm_model.run_id == run_id).all()
        return [self._to_domain(orm_instance) for orm_instance in orm_instances]


class FindingRepository(BaseRepository[Finding, FindingModel]):
    """Repository for Finding entities."""

    def __init__(self, session: Session):
        super().__init__(session, FindingModel, Finding)

    def get_by_run(self, run_id: UUID) -> list[Finding]:
        """Get findings by run ID.

        Args:
            run_id: Run ID.

        Returns:
            List of findings.
        """
        orm_instances = self.session.query(self.orm_model).filter(self.orm_model.run_id == run_id).all()
        return [self._to_domain(orm_instance) for orm_instance in orm_instances]

    def get_by_severity(self, severity: str) -> list[Finding]:
        """Get findings by severity.

        Args:
            severity: Severity level.

        Returns:
            List of findings.
        """
        orm_instances = self.session.query(self.orm_model).filter(self.orm_model.severity == severity).all()
        return [self._to_domain(orm_instance) for orm_instance in orm_instances]


class AssetRepository(BaseRepository[Asset, AssetModel]):
    """Repository for Asset entities."""

    def __init__(self, session: Session):
        super().__init__(session, AssetModel, Asset)

    def get_by_job(self, job_id: UUID) -> list[Asset]:
        """Get assets by job ID.

        Args:
            job_id: Job ID.

        Returns:
            List of assets.
        """
        orm_instances = self.session.query(self.orm_model).filter(self.orm_model.job_id == job_id).all()
        return [self._to_domain(orm_instance) for orm_instance in orm_instances]


class IOCRepository(BaseRepository[IOC, IOCModel]):
    """Repository for IOC entities."""

    def __init__(self, session: Session):
        super().__init__(session, IOCModel, IOC)

    def get_by_type(self, ioc_type: str) -> list[IOC]:
        """Get IOCs by type.

        Args:
            ioc_type: IOC type.

        Returns:
            List of IOCs.
        """
        orm_instances = self.session.query(self.orm_model).filter(self.orm_model.type == ioc_type).all()
        return [self._to_domain(orm_instance) for orm_instance in orm_instances]

    def get_active(self) -> list[IOC]:
        """Get active IOCs.

        Returns:
            List of active IOCs.
        """
        orm_instances = self.session.query(self.orm_model).filter(self.orm_model.is_active).all()
        return [self._to_domain(orm_instance) for orm_instance in orm_instances]


class UserRepository(BaseRepository[User, UserModel]):
    """Repository for User entities."""

    def __init__(self, session: Session):
        super().__init__(session, UserModel, User)

    def get_by_username(self, username: str) -> User | None:
        """Get user by username.

        Args:
            username: Username.

        Returns:
            User or None.
        """
        orm_instance = self.session.query(self.orm_model).filter(self.orm_model.username == username).first()
        return self._to_domain(orm_instance) if orm_instance else None

    def get_by_email(self, email: str) -> User | None:
        """Get user by email.

        Args:
            email: Email address.

        Returns:
            User or None.
        """
        orm_instance = self.session.query(self.orm_model).filter(self.orm_model.email == email).first()
        return self._to_domain(orm_instance) if orm_instance else None

    def get_active_users(self) -> list[User]:
        """Get all active users.

        Returns:
            List of active users.
        """
        orm_instances = self.session.query(self.orm_model).filter(self.orm_model.disabled is False).all()
        return [self._to_domain(orm_instance) for orm_instance in orm_instances]


class APIKeyRepository(BaseRepository[APIKey, APIKeyModel]):
    """Repository for APIKey entities."""

    def __init__(self, session: Session):
        super().__init__(session, APIKeyModel, APIKey)

    def get_by_key_hash(self, key_hash: str) -> APIKey | None:
        """Get API key by hash.

        Args:
            key_hash: Hashed API key.

        Returns:
            APIKey or None.
        """
        orm_instance = self.session.query(self.orm_model).filter(self.orm_model.key_hash == key_hash).first()
        return self._to_domain(orm_instance) if orm_instance else None

    def get_by_user(self, user_id: UUID) -> list[APIKey]:
        """Get API keys by user ID.

        Args:
            user_id: User ID.

        Returns:
            List of API keys.
        """
        orm_instances = self.session.query(self.orm_model).filter(self.orm_model.user_id == user_id).all()
        return [self._to_domain(orm_instance) for orm_instance in orm_instances]

    def get_active_keys(self, user_id: UUID) -> list[APIKey]:
        """Get active API keys by user ID.

        Args:
            user_id: User ID.

        Returns:
            List of active API keys.
        """
        orm_instances = (
            self.session.query(self.orm_model)
            .filter(self.orm_model.user_id == user_id, self.orm_model.is_active is True)
            .all()
        )
        return [self._to_domain(orm_instance) for orm_instance in orm_instances]
