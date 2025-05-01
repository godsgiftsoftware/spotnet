"""Module provides functionallity for managing database views in sqlalchemy"""

import sqlalchemy as sa
from sqlalchemy.ext import compiler
from sqlalchemy.schema import ExecutableDDLElement
from sqlalchemy.sql.compiler import DDLCompiler


class CreateView(ExecutableDDLElement):
    """Class used to create view in db schema"""

    def __init__(self, name: str, selectable: sa.Select):
        self.name = name
        self.selectable = selectable


class DropView(ExecutableDDLElement):
    """Class used to drop view in db schema"""

    def __init__(self, name):
        self.name = name


@compiler.compiles(CreateView)
def _create_view(element: sa.Table, ddlcompiler: DDLCompiler, **kw):
    """Provides sql query to create view"""
    return "CREATE VIEW %s AS %s" % (
        element.name,
        ddlcompiler.sql_compiler.process(element.selectable, literal_binds=True),
    )


@compiler.compiles(DropView)
def _drop_view(element: sa.Table, ddlcompiler: DDLCompiler, **kw):
    """Provides sql query to drop view"""
    return "DROP VIEW %s" % (element.name)


def _view_exists(ddl, target, bind, **kw):
    """Check if view exists in schema"""
    return ddl.name in sa.inspect(bind).get_view_names()


def _view_doesnt_exist(ddl, target, connection, **kw):
    """Check if view doesnt exist in schema"""
    return not _view_exists(ddl, target, connection, **kw)


def create_view(name: str, metadata: sa.MetaData, selectable: sa.Select):
    """
    Creates new table object using columns from provided statement(selectable).
    Adds listeners for metadata to create and drop view on corresponding metadata operations
    """
    t = sa.table(
        name,
        *(
            sa.Column(c.name, c.type, primary_key=c.primary_key)
            for c in selectable.selected_columns
        ),
    )
    t.primary_key.update(c for c in t.c if c.primary_key)

    sa.event.listen(
        metadata,
        "after_create",
        CreateView(name, selectable).execute_if(callable_=_view_doesnt_exist),
    )
    sa.event.listen(
        metadata,
        "before_drop",
        DropView(name).execute_if(callable_=_view_exists),
    )
    return t
