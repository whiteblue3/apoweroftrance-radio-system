from django.utils.translation import ugettext_lazy as _

ACCESS_TYPE_AUTHENTICATE = 'authenticate'
ACCESS_TYPE_LOGOUT = 'logout'

ACCESS_STATUS_SUCCESSFUL = 'success'
ACCESS_STATUS_FAIL = 'fail'
ACCESS_STATUS_FAIL_USER_NOT_EXIST = 'fail_user_not_exist'
ACCESS_STATUS_FAIL_USER_INACTIVE = 'fail_user_inactive'

ACCESS_TYPE = (
    (None, _('None')),
    (ACCESS_TYPE_AUTHENTICATE, _('Authenticate')),
    (ACCESS_TYPE_LOGOUT, _('Logout')),
)

ACCESS_STATUS = (
    (None, _('None')),
    (ACCESS_STATUS_SUCCESSFUL, _('Success')),
    (ACCESS_STATUS_FAIL, _('Fail')),
    (ACCESS_STATUS_FAIL_USER_NOT_EXIST, _('Fail because user does not exist')),
    (ACCESS_STATUS_FAIL_USER_INACTIVE, _('Fail because user is inactive'))
)
