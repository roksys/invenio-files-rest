# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Admin model views for PersistentIdentifier."""

from __future__ import absolute_import, print_function

from flask import current_app, url_for
from flask_admin.contrib.sqla import ModelView
from flask_wtf import Form
from invenio_admin.filters import FilterConverter
from invenio_admin.forms import LazyChoices
from markupsafe import Markup
from wtforms.validators import ValidationError

from .models import Bucket, FileInstance, Location, ObjectVersion, slug_pattern


def _(x):
    """Identity function for string extraction."""
    return x


def require_slug(form, field):
    """Validate location name."""
    if not slug_pattern.match(field.data):
        raise ValidationError(_("Invalid location name."))


def link(text, link_func):
    """Generate a object formatter for links.."""
    def object_formatter(v, c, m, p):
        """Format object view link."""
        return Markup('<a href="{0}">{1}</a>'.format(
            link_func(m), text))
    return object_formatter


class LocationModelView(ModelView):
    """ModelView for the locations."""

    filter_converter = FilterConverter()
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    column_formatters = dict(
        buckets=link('Buckets', lambda o: url_for(
            'bucket.index_view', flt2_2=o.name))
    )
    column_details_list = (
        'name', 'uri', 'default', 'created', 'updated', 'buckets')
    column_list = ('name', 'uri', 'default', 'created', 'updated', 'buckets')
    column_labels = dict(
        id=_('ID'),
        uri=_('URI'),
    )
    column_filters = ('default', 'created', 'updated')
    column_searchable_list = ('uri', 'name')
    column_default_sort = 'name'
    form_base_class = Form
    form_columns = ('name', 'uri', 'default', )
    form_args = dict(
        name=dict(validators=[require_slug])
    )
    page_size = 25


class BucketModelView(ModelView):
    """ModelView for the buckets."""

    filter_converter = FilterConverter()
    can_create = True
    can_delete = False
    can_edit = True
    can_view_details = True
    column_formatters = dict(
        objects=link('Objects', lambda o: url_for(
            'objectversion.index_view', flt0_0=o.id, flt1_37=1, sort=1)),
        object_versions=link('Object Versions', lambda o: url_for(
            'objectversion.index_view', flt0_0=o.id, flt1_29=1, sort=1)),
    )
    column_details_list = (
        'id', 'location', 'default_storage_class', 'deleted', 'locked',
        'created', 'updated', 'objects', 'object_versions'
    )
    column_list = (
        'id', 'location', 'default_storage_class', 'deleted', 'locked', 'size',
        'created', 'updated', 'objects',
    )
    column_labels = dict(
        id=_('UUID'),
        default_location=_('Location'),
        pid_provider=_('Storage Class'),
    )
    column_filters = (
        # Change of order affects Location.column_formatters!
        'location.name', 'default_storage_class', 'deleted', 'locked', 'size',
        'created', 'updated',
    )
    column_default_sort = ('updated', True)
    form_base_class = Form
    form_columns = ('location', 'default_storage_class', 'locked', 'deleted', )
    form_choices = dict(
        default_storage_class=LazyChoices(lambda: current_app.config[
            'FILES_REST_STORAGE_CLASS_LIST'].items()))
    page_size = 25


class ObjectModelView(ModelView):
    """ModelView for the objects."""

    filter_converter = FilterConverter()
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    column_formatters = dict(
        file_instance=link('File', lambda o: url_for(
            'fileinstance.index_view', flt0_0=o.file_id)),
        versions=link('Versions', lambda o: url_for(
            'objectversion.index_view',
            sort=7, desc=1, flt0_0=o.bucket_id, flt1_29=o.key)),
        bucket_objs=link('Objects', lambda o: url_for(
            'objectversion.index_view',
            flt0_0=o.bucket_id, flt1_37=1, sort=1)),
    )
    column_labels = {
        'version_id': _('Version'),
        'file_id': _('File UUID'),
        'file.uri': _('URI'),
        'file.size': _('Size'),
        'is_deleted': _('Deleted'),
        'file.checksum': _('Checksum'),
        'file.read_only': _('Read only'),
        'file.storage_class': _('Storage class'),
        'bucket_objs': _("Objects"),
        'file_instance': _("File"),
    }
    column_list = (
        'bucket', 'key', 'version_id', 'file.uri', 'is_head', 'is_deleted',
        'file.size', 'created', 'updated', 'versions', 'bucket_objs',
        'file_instance')
    column_searchable_list = ('key', )
    column_details_list = (
        'bucket', 'key', 'version_id', 'file_id', 'file.uri', 'file.checksum',
        'file.size', 'file.storage_class', 'is_head', 'is_deleted', 'created',
        'updated', 'file_instance', 'versions')
    column_filters = (
        # Order affects column_formatters in other model views.
        'bucket.id', 'bucket.locked', 'bucket.deleted', 'bucket.location.name',
        'file_id', 'file.checksum', 'file.storage_class', 'file.read_only',
        'key', 'version_id', 'is_head', 'file.size', 'created', 'updated', )
    column_sortable_list = (
        'key', 'file.uri', 'is_head', 'file.size', 'created', 'updated')
    column_default_sort = ('updated', True)
    page_size = 25


class FileInstanceModelView(ModelView):
    """ModelView for the objects."""

    filter_converter = FilterConverter()
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    column_formatters = dict(
        objects=link('Objects', lambda o: url_for(
            'objectversion.index_view', flt3_12=o.id)),
    )
    column_labels = dict(
        id=_('ID'),
        uri=_('URI'),
    )
    column_list = (
        'id', 'uri', 'storage_class', 'size', 'checksum', 'read_only',
        'created', 'updated', 'objects')
    column_searchable_list = ('uri', 'size', 'checksum', )
    column_details_list = (
        'id', 'uri', 'storage_class', 'size', 'checksum', 'read_only',
        'created', 'updated', 'objects', )
    column_filters = (
        'id', 'uri', 'storage_class', 'size', 'checksum', 'read_only',
        'created', 'updated')
    column_default_sort = ('updated', True)
    page_size = 25


location_adminview = dict(
    modelview=LocationModelView,
    model=Location,
    category=_('Files'))
bucket_adminview = dict(
    modelview=BucketModelView,
    model=Bucket,
    category=_('Files'))
object_adminview = dict(
    modelview=ObjectModelView,
    model=ObjectVersion,
    category=_('Files'))
fileinstance_adminview = dict(
    modelview=FileInstanceModelView,
    model=FileInstance,
    category=_('Files'))
