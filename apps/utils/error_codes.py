from django.db.models import TextChoices


class ApiErrors(TextChoices):
    BAD_CREDENTIALS = "error_login_bad_credentials"
    COMMON_PASSWORD_VALIDATION = "error_password_too_common"  # noqa S105
    FIELD_IS_REQUIRED = "error_field_is_required"
    INVALID_APP_VERSION_VALUE = "error_invalid_app_version_value"
    INVALID_EMAIL = "error_invalid_email"
    MINIMUM_LENGTH_VALIDATION = "error_password_too_short"
    NEW_EMAIL_SAME_AS_OLD_ONE = "error_new_email_same_as_old_one"
    NO_SUCH_LANGUAGE = "error_no_such_language"
    NUMERIC_PASSWOD_VALIDATION = "error_password_entirely_numeric"  # noqa S105
    PASSWORDS_NOT_EQUAL = "error_passwords_not_equal"
    PASSWORD_IS_INCORRECT = "error_password_is_incorrect"  # noqa S105
    RESET_PASSWORD_KEY_EXPIRED = "error_reset_password_key_expired"  # noqa S105
    USER_ALREADY_VERIFIED = "error_verify_already_verified"
    USER_ATRIBUTE_SIMILARITY_VALIDATION = "error_password_too_similar_to_email"
    USER_DATETIME_CLAIM_CHANGED = "error_user_datetime_claim_changed"
    USER_DOES_NOT_EXIST = "error_user_does_not_exist"
    USER_DOES_NOT_HAVE_FIRST_OR_LAST_NAME_SET = "error_this_user_does_not_have_first_or_last_name_set"
    USER_EMAIL_NOT_VERIFIED = "error_login_user_email_not_verified"
    USER_IS_NOT_ACTIVE = "error_user_is_not_active"
    VERIFIED_USER_ALREADY_EXISTS = "error_verified_user_already_exists"
