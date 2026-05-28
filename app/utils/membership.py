INTERNAL_ACCESS_TYPES = {'internal', 'admin_created'}


def is_internal_membership(membership):
    return bool(
        membership
        and membership.is_active
        and membership.access_type in INTERNAL_ACCESS_TYPES
    )


def can_access_internal_org_features(user, membership):
    if not user or not membership or not membership.is_active:
        return False

    if user.user_type in ['main_co_admin', 'co_admin', 'super_admin']:
        return True

    return user.user_type == 'student' and is_internal_membership(membership)
