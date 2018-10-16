# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2018 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
import ConfigParser
import os
from optparse import make_option

from geonode.base.management.commands import helpers


class Config(helpers.Config):

    option = make_option(
        '-c',
        '--config',
        type="string",
        help='Use custom settings.ini configuration file')

    qgis_server_option_list = (
        make_option(
            '--qgis-server-data-dir',
            dest="qs_data_dir",
            type="string",
            default=None,
            help="QGIS Server data directory"), )

    def load_options(self, options):
        self.qs_data_dir = options.get('qs_data_dir', None) or self.qs_data_dir

    def load_settings(self, settings_path=None):
        if not settings_path:
            settings_dir = os.path.abspath(os.path.dirname(__file__))
            settings_path = os.path.join(settings_dir, 'settings.ini')

        config = ConfigParser.ConfigParser()
        config.read(settings_path)

        self.pg_dump_cmd = config.get('database', 'pgdump')
        self.pg_restore_cmd = config.get('database', 'pgrestore')

        self.qs_data_dir = config.get('qgis_server', 'datadir')

        self.app_names = config.get('fixtures', 'apps').split(',')
        self.dump_names = config.get('fixtures', 'dumps').split(',')
        self.migrations = config.get('fixtures', 'migrations').split(',')
        self.manglers = config.get('fixtures', 'manglers').split(',')
