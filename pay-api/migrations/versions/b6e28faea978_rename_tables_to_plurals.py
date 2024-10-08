"""rename tables to plurals 

Revision ID: b6e28faea978
Revises: 90afcc0d6d9f
Create Date: 2021-01-25 21:50:58.043768

"""

import re

from alembic import op
from sqlalchemy import MetaData, create_engine, inspect
from sqlalchemy.engine import reflection

# revision identifiers, used by Alembic.
from sqlalchemy.engine.reflection import Inspector


VERSION = "_version"

# revision identifiers, used by Alembic.
revision = "b6e28faea978"
down_revision = "90afcc0d6d9f"
branch_labels = None
depends_on = None

###
# get_pk_constraint

table_mapping = {
    "cfs_account": "cfs_accounts",
    "cfs_account_status_code": "cfs_account_status_codes",
    "corp_type": "corp_types",
    "daily_payment_batch": "daily_payment_batches",
    "daily_payment_batch_link": "daily_payment_batch_links",
    "distribution_code": "distribution_codes",
    "distribution_code_link": "distribution_code_links",
    "ejv_batch": "ejv_batches",
    "ejv_batch_link": "ejv_batch_links",
    "error_code": "error_codes",
    "fee_code": "fee_codes",
    "fee_schedule": "fee_schedules",
    "filing_type": "filing_types",
    "invoice": "invoices",
    "invoice_batch": "invoice_batches",
    "invoice_batch_link": "invoice_batch_links",
    "invoice_reference": "invoice_references",
    "invoice_reference_status_code": "invoice_reference_status_codes",
    "invoice_status_code": "invoice_status_codes",
    "line_item_status_code": "line_item_status_codes",
    "notification_status_code": "notification_status_codes",
    "payment": "payments",
    "payment_account": "payment_accounts",
    "payment_line_item": "payment_line_items",
    "payment_method": "payment_methods",
    "payment_status_code": "payment_status_codes",
    "payment_system": "payment_systems",
    "payment_transaction": "payment_transactions",
    "receipt": "receipts",
    "statement": "statements",
    "transaction_status_code": "transaction_status_codes",
}

skip_table = ["alembic", "activity", "transaction"]


def upgrade():
    """
    have to change
        1. primary key
        2. index name
        3. sequence name
        4. foriegn key name

    """

    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    metadata = MetaData()
    metadata.reflect(conn)

    table: str
    for table in tables:
        if table in skip_table or table.endswith(VERSION):
            continue
        print("<<<<Processing starting for table", table)
        _rename_obj(inspector, metadata, table, table_mapping, tables)
        print("Processing ended for table>>>", table)


def downgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    metadata = MetaData()
    metadata.reflect(conn)
    table_mapping_reversed = {y: x for x, y in table_mapping.items()}
    table: str
    for table in tables:
        if table in skip_table or table.endswith(VERSION):
            continue
        print("<<<<Processing starting for table", table)
        _rename_obj(inspector, metadata, table, table_mapping_reversed, tables)
        print("Processing ended for table>>>", table)


def _rename_obj(inspector, metadata, table: str, name_dict, tables):
    _rename_fks(inspector, table, table_mapping)
    new_table_name: str = name_dict.get(table, "")
    if new_table_name:
        print(f"New name found for Table : {table} to {new_table_name}")
        _rename_indexes(inspector, new_table_name, table)
        _rename_pk(inspector, new_table_name, table)
        _rename_sequence(metadata, new_table_name, table)
        _rename_table(table, new_table_name)
        versioned_table_name = _suffix_version(table)
        if versioned_table_name in tables:
            versioned_table_new_name = _suffix_version(new_table_name)
            _rename_indexes(inspector, versioned_table_new_name, versioned_table_name)
            _rename_table(versioned_table_name, versioned_table_new_name)

        print(f"Renaming Table Done for: {table} to {new_table_name}")


def _suffix_version(table):
    return table + VERSION


def _rename_table(table, new_table_name):
    print(f"\t<<<<<<<<Renaming Table : {table} to {new_table_name} ")
    op.rename_table(table, new_table_name)
    print(f"\tRenaming Done for Table : {table} to {new_table_name} >>>>>>>>>")


def _rename_sequence(m, new_table_name, table):
    """Rename the autogenerated sequnces for the table."""
    id_column = m.tables[table].columns.get("id")
    if id_column is not None and id_column.server_default is not None:
        seq = id_column.server_default.arg.text
        # format is 'nextval(\'org_id_seq\'::regclass)'
        seq_name = re.search(r"nextval\(\'(.*)\'::regclass", seq).group(1)
        new_seq_name = seq_name.replace(table, new_table_name, 1)
        if seq_name != new_seq_name:
            print(
                f"\t<<<<<<<<<Renaming PK : {seq_name} to {new_seq_name} of table {table}"
            )
            op.execute(f"ALTER sequence {seq_name} RENAME TO {new_seq_name}")
            print(
                f"\tRenaming PK : {seq_name} to {new_seq_name} of table {table}>>>>>>>>>>>"
            )


def _rename_pk(inspector, new_table_name, table):
    """Rename primary key.From org_pkey to orgs_pkey"""
    pk_name = inspector.get_pk_constraint(table).get("name")
    new_pk_name = pk_name.replace(table, new_table_name, 1)
    if pk_name != new_pk_name:
        print(f"\t<<<<<<<<<<Renaming PK : {pk_name} to {new_pk_name} of table {table}")
        op.execute(f"ALTER index {pk_name} RENAME TO {new_pk_name}")
        print(
            f"\tRenaming Done for PK : {pk_name} to {new_pk_name} of table {table}>>>>>>>>>"
        )


def _rename_indexes(inspector, new_table_name, table):
    """Rename the indexes.ie ix_org_access_type to ix_orgs_access_type"""
    for index in inspector.get_indexes(table):
        old_index_name = index.get("name")
        new_index_name = old_index_name.replace(table, new_table_name, 1)
        if old_index_name != new_index_name:
            print(
                f"\t<<<<<<Renaming Index : {old_index_name} to {new_index_name} of table {table}"
            )
            op.execute(f"ALTER index {old_index_name} RENAME TO {new_index_name}")
            print(
                f"\tRenaming Index Done for: {old_index_name} to {new_index_name} of table {table}>>>>>>>>"
            )


def _rename_fks(inspector, table: str, name_dict):
    """Rename the forign keys.
    Bit of extra logic is needed becuase the table might not get changed.
    But the referencing table might get a name change and it might be referenced in the FK name.
    ie org_type_code_fkey is a foriegn key on org which refers to org_type table.
    when org_type is turned into org_types ,fk is also changed
    """
    foreign_keys = inspector.get_foreign_keys(table)
    for fk in foreign_keys:
        fk_name = fk.get("name")
        referred_table = fk.get("referred_table")
        referred_table_new_name = name_dict.get(referred_table, "")
        if referred_table_new_name:
            new_fk_name = fk_name.replace(referred_table, referred_table_new_name)
            if fk_name != new_fk_name:
                print(
                    f"\t<<<<<<<<<<Renaming Foriegn Key : {fk_name} to {new_fk_name} of table {table}"
                )
                op.execute(
                    f'ALTER table "{table}" RENAME CONSTRAINT "{fk_name}" TO {new_fk_name}'
                )
                print(
                    f"\tRenaming done for Foriegn Key : {fk_name} to {new_fk_name} of table {table}>>>>>>>>>>"
                )
