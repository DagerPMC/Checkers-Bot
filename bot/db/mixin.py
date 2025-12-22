from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )


class CreatedUpdatedAtMixin(CreatedAtMixin, UpdatedAtMixin):
    pass
