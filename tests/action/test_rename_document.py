import pytest

from mongoengine_migrate.actions import RenameDocument
from mongoengine_migrate.exceptions import SchemaError


class TestRenameDocument:
    def test_forward__should_do_nothing(self, load_fixture, test_db, dump_db):
        schema = load_fixture('schema1').get_schema()
        dump = dict(dump_db())

        action = RenameDocument('Schema1Doc1', new_name='NewNameDoc')
        action.prepare(test_db, schema)

        action.run_forward()

        assert dump == dict(dump_db())

    def test_backward__should_do_nothing(self, load_fixture, test_db, dump_db):
        schema = load_fixture('schema1').get_schema()
        dump = dict(dump_db())

        action = RenameDocument('Schema1Doc1', new_name='NewNameDoc')
        action.prepare(test_db, schema)

        action.run_backward()

        assert dump == dict(dump_db())

    def test_prepare__if_such_document_is_not_in_schema__should_raise_error(self,
                                                                            load_fixture,
                                                                            test_db):
        schema = load_fixture('schema1').get_schema()
        del schema['Schema1Doc1']

        action = RenameDocument('Schema1Doc1', new_name='NewNameDoc')

        with pytest.raises(SchemaError):
            action.prepare(test_db, schema)