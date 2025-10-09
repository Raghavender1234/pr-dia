"""Add explain_calls to student_ai_usage

Revision ID: 975ae287cd99
Revises: 4ef3e3b8a054
Create Date: 2025-10-02 09:23:25.048764
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '975ae287cd99'
down_revision = '4ef3e3b8a054'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    cols = insp.get_columns('student_ai_usage')
    colmap = {c['name']: c for c in cols}

    if 'explain_calls' not in colmap:
        # 1) add nullable first to avoid immediate failures
        op.add_column(
            'student_ai_usage',
            sa.Column('explain_calls', sa.Integer(), nullable=True)
        )
        # 2) backfill to 0
        op.execute("UPDATE student_ai_usage SET explain_calls = 0 WHERE explain_calls IS NULL")
        # 3) enforce NOT NULL + server default 0 (then drop server default to rely on app default)
        with op.batch_alter_table('student_ai_usage') as batch_op:
            batch_op.alter_column(
                'explain_calls',
                existing_type=sa.INTEGER(),
                nullable=False,
                server_default='0'
            )
        # 4) optional: remove DB-level default so the ORM default=0 is the authority
        with op.batch_alter_table('student_ai_usage') as batch_op:
            batch_op.alter_column('explain_calls', server_default=None)

    else:
        # Column exists: make sure it conforms to NOT NULL with 0s
        if colmap['explain_calls'].get('nullable', True):
            op.execute("UPDATE student_ai_usage SET explain_calls = 0 WHERE explain_calls IS NULL")
            with op.batch_alter_table('student_ai_usage') as batch_op:
                batch_op.alter_column(
                    'explain_calls',
                    existing_type=sa.INTEGER(),
                    nullable=False,
                    server_default='0'
                )
            # optional: drop the default again
            with op.batch_alter_table('student_ai_usage') as batch_op:
                batch_op.alter_column('explain_calls', server_default=None)


def downgrade():
    # Drop the column if it exists (idempotent)
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c['name'] for c in insp.get_columns('student_ai_usage')}
    if 'explain_calls' in cols:
        op.drop_column('student_ai_usage', 'explain_calls')
