"""rush_fee_code

Revision ID: c871202927f0
Revises: 5b1ae231f7d2
Create Date: 2021-07-13 14:34:48.482182

"""
from datetime import date

from alembic import op
from sqlalchemy import Date, String, Float
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = 'c871202927f0'
down_revision = '5b1ae231f7d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    distribution_code_link_table = table('distribution_code_links',
                                         column('distribution_code_id', String),
                                         column('fee_schedule_id', String)
                                         )
    filing_type_table = table('filing_types',
                              column('code', String),
                              column('description', String)
                              )
    fee_code_table = table('fee_codes',
                           column('code', String),
                           column('amount', Float)
                           )
    op.bulk_insert(
        fee_code_table,
        [
            {'code': 'EN204', 'amount': 33}
        ]
    )
    op.bulk_insert(
        filing_type_table,
        [
            {'code': 'WILLRUSH', 'description': 'Rush Fee'}
        ]
    )

    fee_schedule_table = table('fee_schedules',
                               column('filing_type_code', String),
                               column('corp_type_code', String),
                               column('fee_code', String),
                               column('fee_start_date', Date),
                               column('fee_end_date', Date),
                               column('future_effective_fee_code', String),
                               column('priority_fee_code', String),
                               column('service_fee_code', String)
                               )

    op.bulk_insert(
        fee_schedule_table,
        [
            {
                "filing_type_code": "WILLRUSH",
                "corp_type_code": "VS",
                "fee_code": "EN204",
                "fee_start_date": date.today(),
                "fee_end_date": None,
                "future_effective_fee_code": None,
                "priority_fee_code": None,
                "service_fee_code": "TRF01"
            }
        ]
    )
    # Now find out the distribution code for other BCINC and map it to them.
    distribution_code_id_query = "select dc.distribution_code_id from distribution_codes dc " \
                                 "where upper(dc.name) = 'VITAL STATISTICS' and dc.start_date <= CURRENT_DATE " \
                                 "and (dc.end_date is null or dc.end_date > CURRENT_DATE)"
    conn = op.get_bind()
    res = conn.execute(distribution_code_id_query)
    distribution_code_id = res.fetchall()[0][0]
    res = conn.execute(
        f"select fee_schedule_id from fee_schedules where corp_type_code='VS' and filing_type_code='WILLRUSH'")
    fee_schedule_id = res.fetchall()[0][0]
    distr_code_link = [{
        'distribution_code_id': distribution_code_id,
        'fee_schedule_id': fee_schedule_id
    }]
    op.bulk_insert(distribution_code_link_table, distr_code_link)
    op.execute("update fee_schedules set priority_fee_code=null where corp_type_code='VS'")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        "DELETE FROM distribution_code_links where fee_schedule_id in "
        "(select fee_schedule_id from fee_schedules where filing_type_code='WILLRUSH' and corp_type_code = 'VS')")
    op.execute("DELETE FROM fee_schedules WHERE filing_type_code='WILLRUSH' and corp_type_code='VS'")
    op.execute("DELETE FROM filing_types WHERE code='WILLRUSH'")

    op.execute("DELETE FROM fee_codes WHERE code = 'EN204'")
    op.execute("update fee_schedules set priority_fee_code='PRI02' where corp_type_code='VS'")

    # ### end Alembic commands ###
