__all__ = [
    'check_empty_result',
    'mongo_version'
]

import functools

from pymongo.collection import Collection

from mongoengine_migrate.exceptions import InconsistencyError
from mongoengine_migrate.updater import DocumentUpdater, FallbackDocumentUpdater
from . import flags


def check_empty_result(collection: Collection, db_field: str, find_filter: dict) -> None:
    """
    Find records in collection satisfied to a given filter expression
    and raise error if anything found
    :param collection: pymongo collection object to find in
    :param db_field: collection field name
    :param find_filter: collection.find() method filter argument
    :raises MigrationError: if any records found
    """
    bad_records = list(collection.find(find_filter, limit=3))
    if bad_records:
        examples = (
            '{{_id: {},...{}: {}}}'.format(
                x.get("_id", "unknown"), db_field, x.get(db_field, "unknown")
            ) for x in bad_records
        )
        raise InconsistencyError(
            "Field {}.{} in some records has wrong values. "
            "First several examples: {}".format(collection.name, db_field, ','.join(examples))
        )


def mongo_version(min_version: str = None, max_version: str = None):
    """
    Decorator restrict decorated change method execution by
    MongoDB version.

    If current db version is out of specified range then instead of
    original DocumentUpdater instance, its fallback variant will be
    passed to a method
    :param min_version: Minimum MongoDB version (including)
    :param max_version: Maximum MongoDB version (excluding)
    :return:
    """
    assert min_version or max_version
    # TODO: add warning if monge version is not in range

    def dec(f):
        @functools.wraps(f)
        def w(*args, **kwargs):
            invalid = min_version and flags.mongo_version < min_version \
                or max_version and flags.mongo_version >= max_version

            if invalid:
                # Inject fallback updater instead of original updater
                # on 0th place (general function) or 1st (class method)
                for ind in range(2):
                    if len(args) > ind and isinstance(args[ind], DocumentUpdater):
                        args = args[:ind] + (FallbackDocumentUpdater(args[ind]),) + args[ind + 1:]
                        break
                else:
                    raise TypeError(
                        "Could not find DocumentUpdater in arguments of {}".format(f.__name__)
                    )

            return f(*args, **kwargs)

        return w
    return dec
