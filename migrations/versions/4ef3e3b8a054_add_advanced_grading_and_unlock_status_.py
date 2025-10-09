"""Add advanced grading and unlock status to tests

Revision ID: 4ef3e3b8a054
Revises: ddb30a0f0235
Create Date: 2025-09-26 13:54:38.372998
"""
from alembic import op
import sqlalchemy as sa

# --- Revision identifiers ---
revision = '4ef3e3b8a054'
down_revision = 'ddb30a0f0235'
branch_labels = None
depends_on = None


def upgrade():
    # student_question_responses
    with op.batch_alter_table('student_question_responses', schema=None) as batch_op:
        # add NOT NULL column with a temporary server_default to backfill existing rows
        batch_op.add_column(
            sa.Column('grading_status', sa.String(length=20), nullable=False, server_default='pending')
        )
        batch_op.add_column(sa.Column('points_awarded', sa.Numeric(6, 2), nullable=True))
        batch_op.add_column(sa.Column('grader_comments', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('graded_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('graded_by_admin_id', sa.Integer(), nullable=True))
        # FK target should match your schema; autogenerate used 'users'
        batch_op.create_foreign_key(
            'fk_sqr_graded_by_user', 'users', ['graded_by_admin_id'], ['id'], ondelete='SET NULL'
        )

    # drop the temporary server_default
    op.alter_column(
        'student_question_responses',
        'grading_status',
        server_default=None,
        existing_type=sa.String(length=20),
        existing_nullable=False,
    )

    # student_test_attempts
    # Make these nullable at creation time to avoid NOT NULL violations on existing rows.
    with op.batch_alter_table('student_test_attempts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_unlocked', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('unlocked_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('unlocked_by_admin_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('was_pending_grading', sa.Boolean(), nullable=True))
        batch_op.create_foreign_key(
            'fk_sta_unlocked_by_user', 'users', ['unlocked_by_admin_id'], ['id'], ondelete='SET NULL'
        )

    # (optional) if you truly want NOT NULL booleans, backfill first, then enforce:
    # op.execute("UPDATE student_test_attempts SET is_unlocked = false WHERE is_unlocked IS NULL")
    # op.execute("UPDATE student_test_attempts SET was_pending_grading = false WHERE was_pending_grading IS NULL")
    # op.alter_column('student_test_attempts', 'is_unlocked', nullable=False, existing_type=sa.Boolean())
    # op.alter_column('student_test_attempts', 'was_pending_grading', nullable=False, existing_type=sa.Boolean())


def downgrade():
    with op.batch_alter_table('student_test_attempts', schema=None) as batch_op:
        batch_op.drop_constraint('fk_sta_unlocked_by_user', type_='foreignkey')
        batch_op.drop_column('was_pending_grading')
        batch_op.drop_column('unlocked_by_admin_id')
        batch_op.drop_column('unlocked_at')
        batch_op.drop_column('is_unlocked')

    with op.batch_alter_table('student_question_responses', schema=None) as batch_op:
        batch_op.drop_constraint('fk_sqr_graded_by_user', type_='foreignkey')
        batch_op.drop_column('graded_by_admin_id')
        batch_op.drop_column('graded_at')
        batch_op.drop_column('grader_comments')
        batch_op.drop_column('points_awarded')
        batch_op.drop_column('grading_status')
