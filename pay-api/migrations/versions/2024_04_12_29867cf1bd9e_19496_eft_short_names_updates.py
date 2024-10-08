"""19496-eft-shortname-updates

Revision ID: 29867cf1bd9e
Revises: 52ed2340a43c
Create Date: 2024-04-12 10:21:53.863572

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "29867cf1bd9e"
down_revision = "52ed2340a43c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    # Table to support multiple accounts linked to a short name with different statuses
    op.create_table(
        "eft_short_name_links",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("eft_short_name_id", sa.Integer(), nullable=False),
        sa.Column("auth_account_id", sa.String(length=50), nullable=False),
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.Column("status_code", sa.String(length=25), nullable=False),
        sa.Column("updated_by", sa.String(length=100), nullable=True),
        sa.Column("updated_by_name", sa.String(length=100), nullable=True),
        sa.Column("updated_on", sa.DateTime(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["eft_short_name_id"],
            ["eft_short_names.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sqlite_autoincrement=True,
    )
    with op.batch_alter_table("eft_short_name_links", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_eft_short_name_links_auth_account_id"),
            ["auth_account_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_eft_short_name_links_eft_short_name_id"),
            ["eft_short_name_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_eft_short_name_links_status_code"),
            ["status_code"],
            unique=False,
        )

    op.create_table(
        "eft_short_name_links_history",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column(
            "eft_short_name_id", sa.Integer(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "auth_account_id", sa.String(length=50), autoincrement=False, nullable=False
        ),
        sa.Column("created_on", sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column(
            "status_code", sa.String(length=25), autoincrement=False, nullable=False
        ),
        sa.Column(
            "updated_by", sa.String(length=100), autoincrement=False, nullable=True
        ),
        sa.Column(
            "updated_by_name", sa.String(length=100), autoincrement=False, nullable=True
        ),
        sa.Column("updated_on", sa.DateTime(), autoincrement=False, nullable=True),
        sa.Column("version", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("changed", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["eft_short_name_id"],
            ["eft_short_names.id"],
        ),
        sa.PrimaryKeyConstraint("id", "version"),
        sqlite_autoincrement=True,
    )

    with op.batch_alter_table("eft_short_name_links_history", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_eft_short_name_links_history_auth_account_id"),
            ["auth_account_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_eft_short_name_links_history_eft_short_name_id"),
            ["eft_short_name_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_eft_short_name_links_history_status_code"),
            ["status_code"],
            unique=False,
        )

    # Migrate linking information from existing short name table
    op.execute(
        text(
            f"INSERT INTO eft_short_name_links (eft_short_name_id, auth_account_id, created_on, status_code, "
            f"updated_by, updated_by_name, updated_on, version) "
            f"select id, auth_account_id, created_on, 'LINKED', linked_by, linked_by_name, linked_on, 1 "
            f"from eft_short_names where auth_account_id is not null"
        )
    )

    with op.batch_alter_table("eft_short_names", schema=None) as batch_op:
        batch_op.drop_index("ix_eft_short_names_auth_account_id")
        batch_op.drop_column("auth_account_id")
        batch_op.drop_column("linked_by_name")
        batch_op.drop_column("linked_by")
        batch_op.drop_column("linked_on")

    with op.batch_alter_table("eft_short_names_history", schema=None) as batch_op:
        batch_op.drop_index("ix_eft_short_names_history_auth_account_id")
        batch_op.drop_column("auth_account_id")
        batch_op.drop_column("linked_by_name")
        batch_op.drop_column("linked_by")
        batch_op.drop_column("linked_on")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("eft_short_names_history", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "linked_on", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                "linked_by", sa.VARCHAR(length=100), autoincrement=False, nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                "linked_by_name",
                sa.VARCHAR(length=100),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "auth_account_id",
                sa.VARCHAR(length=50),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.create_index(
            "ix_eft_short_names_history_auth_account_id",
            ["auth_account_id"],
            unique=False,
        )

    with op.batch_alter_table("eft_short_names", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "linked_on", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                "linked_by", sa.VARCHAR(length=100), autoincrement=False, nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                "linked_by_name",
                sa.VARCHAR(length=100),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "auth_account_id",
                sa.VARCHAR(length=50),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.create_index(
            "ix_eft_short_names_auth_account_id", ["auth_account_id"], unique=False
        )

    # Restore data from eft short name link table
    op.execute(
        text(
            f"UPDATE eft_short_names esn "
            f"SET auth_account_id = (select auth_account_id from eft_short_name_links esnl where esnl.eft_short_name_id = esn.id),"
            f"linked_on = (select esnl.updated_on from eft_short_name_links esnl where esnl.eft_short_name_id = esn.id),"
            f"linked_by = (select esnl.updated_by from eft_short_name_links esnl where esnl.eft_short_name_id = esn.id),"
            f"linked_by_name = (select esnl.updated_by_name from eft_short_name_links esnl where esnl.eft_short_name_id = esn.id)"
        )
    )

    with op.batch_alter_table("eft_short_name_links_history", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_eft_short_name_links_history_status_code"))
        batch_op.drop_index(
            batch_op.f("ix_eft_short_name_links_history_eft_short_name_id")
        )
        batch_op.drop_index(
            batch_op.f("ix_eft_short_name_links_history_auth_account_id")
        )

    op.drop_table("eft_short_name_links_history")
    with op.batch_alter_table("eft_short_name_links", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_eft_short_name_links_status_code"))
        batch_op.drop_index(batch_op.f("ix_eft_short_name_links_eft_short_name_id"))
        batch_op.drop_index(batch_op.f("ix_eft_short_name_links_auth_account_id"))

    op.drop_table("eft_short_name_links")

    # ### end Alembic commands ###
