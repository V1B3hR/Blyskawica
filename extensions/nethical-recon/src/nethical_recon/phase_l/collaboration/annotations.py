"""
Comments & Annotations
Allows team members to annotate and discuss findings
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class AnnotationType(Enum):
    """Types of annotations"""

    COMMENT = "comment"
    NOTE = "note"
    TAG = "tag"
    STATUS_CHANGE = "status_change"
    ASSIGNMENT = "assignment"


@dataclass
class Annotation:
    """Annotation on a finding or resource"""

    annotation_id: UUID
    resource_type: str  # finding, scan, report, etc.
    resource_id: UUID
    annotation_type: AnnotationType
    content: str
    author_id: UUID
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any]
    parent_id: UUID | None  # For threaded discussions


@dataclass
class Thread:
    """Discussion thread"""

    thread_id: UUID
    resource_type: str
    resource_id: UUID
    title: str
    annotations: list[Annotation]
    participants: list[UUID]
    created_at: datetime
    updated_at: datetime
    is_resolved: bool


class AnnotationManager:
    """
    Manages comments and annotations on findings and resources

    Features:
    - Comment threading
    - Mentions and notifications
    - Status tracking
    - Search and filtering
    """

    def __init__(self):
        """Initialize annotation manager"""
        self._annotations: dict[UUID, Annotation] = {}
        self._threads: dict[UUID, Thread] = {}
        self._resource_annotations: dict[UUID, list[UUID]] = {}  # resource_id -> annotation_ids

    def add_comment(
        self,
        resource_type: str,
        resource_id: UUID,
        content: str,
        author_id: UUID,
        parent_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Annotation:
        """
        Add a comment to a resource

        Args:
            resource_type: Type of resource (finding, scan, etc.)
            resource_id: Resource ID
            content: Comment content
            author_id: User ID of author
            parent_id: Parent annotation ID for threading
            metadata: Additional metadata

        Returns:
            Created annotation
        """
        now = datetime.now()

        annotation = Annotation(
            annotation_id=uuid4(),
            resource_type=resource_type,
            resource_id=resource_id,
            annotation_type=AnnotationType.COMMENT,
            content=content,
            author_id=author_id,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
            parent_id=parent_id,
        )

        self._annotations[annotation.annotation_id] = annotation

        # Add to resource index
        if resource_id not in self._resource_annotations:
            self._resource_annotations[resource_id] = []
        self._resource_annotations[resource_id].append(annotation.annotation_id)

        # Update or create thread
        self._update_thread(annotation)

        return annotation

    def add_note(
        self,
        resource_type: str,
        resource_id: UUID,
        content: str,
        author_id: UUID,
        metadata: dict[str, Any] | None = None,
    ) -> Annotation:
        """Add a note (private comment) to a resource"""
        now = datetime.now()

        annotation = Annotation(
            annotation_id=uuid4(),
            resource_type=resource_type,
            resource_id=resource_id,
            annotation_type=AnnotationType.NOTE,
            content=content,
            author_id=author_id,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
            parent_id=None,
        )

        self._annotations[annotation.annotation_id] = annotation

        if resource_id not in self._resource_annotations:
            self._resource_annotations[resource_id] = []
        self._resource_annotations[resource_id].append(annotation.annotation_id)

        return annotation

    def add_tag(self, resource_type: str, resource_id: UUID, tag: str, author_id: UUID) -> Annotation:
        """Add a tag to a resource"""
        return self.add_note(
            resource_type=resource_type,
            resource_id=resource_id,
            content=tag,
            author_id=author_id,
            metadata={"type": "tag", "tag": tag},
        )

    def update_annotation(self, annotation_id: UUID, content: str) -> Annotation | None:
        """Update an annotation's content"""
        if annotation_id not in self._annotations:
            return None

        annotation = self._annotations[annotation_id]
        annotation.content = content
        annotation.updated_at = datetime.now()

        return annotation

    def delete_annotation(self, annotation_id: UUID) -> bool:
        """Delete an annotation"""
        if annotation_id not in self._annotations:
            return False

        annotation = self._annotations[annotation_id]

        # Remove from resource index
        if annotation.resource_id in self._resource_annotations:
            self._resource_annotations[annotation.resource_id].remove(annotation_id)

        # Remove annotation
        del self._annotations[annotation_id]

        return True

    def get_annotations(self, resource_id: UUID, annotation_type: AnnotationType | None = None) -> list[Annotation]:
        """Get all annotations for a resource"""
        if resource_id not in self._resource_annotations:
            return []

        annotations = [
            self._annotations[ann_id]
            for ann_id in self._resource_annotations[resource_id]
            if ann_id in self._annotations
        ]

        if annotation_type:
            annotations = [a for a in annotations if a.annotation_type == annotation_type]

        return sorted(annotations, key=lambda a: a.created_at)

    def get_thread(self, resource_id: UUID) -> Thread | None:
        """Get discussion thread for a resource"""
        return self._threads.get(resource_id)

    def resolve_thread(self, resource_id: UUID) -> bool:
        """Mark a discussion thread as resolved"""
        if resource_id in self._threads:
            self._threads[resource_id].is_resolved = True
            self._threads[resource_id].updated_at = datetime.now()
            return True
        return False

    def _update_thread(self, annotation: Annotation):
        """Update or create thread for annotation"""
        resource_id = annotation.resource_id

        if resource_id not in self._threads:
            # Create new thread
            self._threads[resource_id] = Thread(
                thread_id=uuid4(),
                resource_type=annotation.resource_type,
                resource_id=resource_id,
                title=f"Discussion on {annotation.resource_type}",
                annotations=[annotation],
                participants=[annotation.author_id],
                created_at=annotation.created_at,
                updated_at=annotation.created_at,
                is_resolved=False,
            )
        else:
            # Update existing thread
            thread = self._threads[resource_id]
            thread.annotations.append(annotation)
            if annotation.author_id not in thread.participants:
                thread.participants.append(annotation.author_id)
            thread.updated_at = annotation.created_at

    def search_annotations(self, query: str, author_id: UUID | None = None) -> list[Annotation]:
        """Search annotations by content"""
        results = []

        for annotation in self._annotations.values():
            if query.lower() in annotation.content.lower():
                if author_id is None or annotation.author_id == author_id:
                    results.append(annotation)

        return sorted(results, key=lambda a: a.created_at, reverse=True)
