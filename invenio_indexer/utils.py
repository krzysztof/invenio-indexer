# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Utility functions for data processing."""

from invenio_records.models import RecordMetadata

from .api import RecordIndexer


def process_models_committed_signal(sender, changes):
    """Handler for indexing record metadata.

    :param sender: The signal sender.
    :param changes: The changes sent: a list of tuple (record, action).
    """
    record_indexer = RecordIndexer()
    op_map = {
        'insert': 'index',
        'update': 'index',
        'delete': 'delete',
    }
    with record_indexer.create_producer() as producer:
        for obj, change in changes:
            if isinstance(obj, RecordMetadata):
                if change in op_map:
                    index, doc_type = record_indexer.record_to_index(
                        obj.json or {}
                    )
                    producer.publish(dict(
                        op=op_map[change],
                        id=str(obj.id),
                        index=index,
                        doc_type=doc_type,
                    ))
