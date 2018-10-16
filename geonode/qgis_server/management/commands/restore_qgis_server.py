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
import os
import shutil
import tempfile
import traceback
from optparse import make_option

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from geonode.base.management.commands import helpers
from geonode.qgis_server.management.commands.helpers import Config
from geonode.utils import designals, resignals


class Command(BaseCommand):

    help = 'Restore the GeoNode application data'

    option_list = BaseCommand.option_list + Config.qgis_server_option_list + (
        Config.option,
        make_option(
            '-i',
            '--ignore-errors',
            action='store_true',
            dest='ignore_errors',
            default=False,
            help='Stop after any errors are encountered.'),
        make_option(
            '-f',
            '--force',
            action='store_true',
            dest='force_exec',
            default=False,
            help='Forces the execution without asking for confirmation.'),
        make_option(
            '--skip-qgis-server',
            action='store_true',
            dest='skip_qgis_server',
            default=False,
            help='Skips QGIS Server backup'),
        make_option(
            '--backup-file',
            dest='backup_file',
            type="string",
            default=None,
            help='Backup archive containing GeoNode data to restore.'),
        make_option(
            '--backup-dir',
            dest='backup_dir',
            type="string",
            default=None,
            help='Backup directory containing GeoNode data to restore.'))

    def restore_qgis_server_backup(self, config, settings, target_folder):
        """Restore QGIS Server project data

        :param config:
        :type config: Config

        :param settings:
        :type settings: dict

        :param target_folder:
        :type target_folder: basestring
        """
        qgis_server_bk_file = os.path.join(
            target_folder, 'qgis_server_data.zip')

        try:

            extract_dir = helpers.unzip_file(
                qgis_server_bk_file, target_folder)

            # Remove current QGIS Server data
            try:
                shutil.rmtree(config.qs_data_dir)
            except:
                pass

            if not os.path.exists(config.qs_data_dir):
                os.makedirs(config.qs_data_dir)

            helpers.copy_tree(extract_dir, config.qs_data_dir)

            print 'Successfully restore QGIS Server data: {}'.format(
                qgis_server_bk_file)
        except BaseException as e:
            print "Could not extract QGIS Server backup"
            raise e

    def handle(self, **options):
        # ignore_errors = options.get('ignore_errors')
        config = Config(options)
        force_exec = options.get('force_exec')
        backup_file = options.get('backup_file')
        skip_qgis_server = options.get('skip_qgis_server')
        backup_dir = options.get('backup_dir')

        if not any([backup_file, backup_dir]):
            raise CommandError("Mandatory option (--backup-file|--backup-dir)")

        if all([backup_file, backup_dir]):
            raise CommandError("Exclusive option (--backup-file|--backup-dir)")

        if backup_file and not os.path.isfile(backup_file):
            raise CommandError("Provided '--backup-file' is not a file")

        if backup_dir and not os.path.isdir(backup_dir):
            raise CommandError("Provided '--backup-dir' is not a directory")

        print "Before proceeding with the Restore, please ensure that:"
        print " 1. The backend (DB or whatever) is accessible and you have rights"
        message = 'WARNING: The restore will overwrite ALL GeoNode data. You want to proceed?'
        if force_exec or helpers.confirm(prompt=message, resp=False):
            target_folder = backup_dir

            if backup_file:
                # Create Target Folder
                restore_folder = os.path.join(tempfile.gettempdir(), 'restore')
                if not os.path.exists(restore_folder):
                    os.makedirs(restore_folder)

                # Extract ZIP Archive to Target Folder
                target_folder = helpers.unzip_file(backup_file, restore_folder)

                # Write Checks
                media_root = settings.MEDIA_ROOT
                media_folder = os.path.join(target_folder, helpers.MEDIA_ROOT)
                static_root = settings.STATIC_ROOT
                static_folder = os.path.join(target_folder, helpers.STATIC_ROOT)
                static_folders = settings.STATICFILES_DIRS
                static_files_folders = os.path.join(target_folder, helpers.STATICFILES_DIRS)
                template_folders = settings.TEMPLATE_DIRS
                template_files_folders = os.path.join(target_folder, helpers.TEMPLATE_DIRS)
                locale_folders = settings.LOCALE_PATHS
                locale_files_folders = os.path.join(target_folder, helpers.LOCALE_PATHS)

                try:
                    print("[Sanity Check] Full Write Access to '{}' ...".format(media_root))
                    helpers.chmod_tree(media_root)
                    print("[Sanity Check] Full Write Access to '{}' ...".format(static_root))
                    helpers.chmod_tree(static_root)
                    for static_files_folder in static_folders:
                        print("[Sanity Check] Full Write Access to '{}' ...".format(static_files_folder))
                        helpers.chmod_tree(static_files_folder)
                    for template_files_folder in template_folders:
                        print("[Sanity Check] Full Write Access to '{}' ...".format(template_files_folder))
                        helpers.chmod_tree(template_files_folder)
                    for locale_files_folder in locale_folders:
                        print("[Sanity Check] Full Write Access to '{}' ...".format(locale_files_folder))
                        helpers.chmod_tree(locale_files_folder)
                except:
                    print("...Sanity Checks on Folder failed. Please make sure that the current user has full WRITE access to the above folders (and sub-folders or files).")
                    print("Reason:")
                    raise

            if not skip_qgis_server:
                self.restore_qgis_server_backup(config, settings, target_folder)
            else:
                print("Skipping QGIS Server backup restore")

            # Prepare Target DB
            try:
                call_command('migrate', interactive=False, load_initial_data=False)

                db_name = settings.DATABASES['default']['NAME']
                db_user = settings.DATABASES['default']['USER']
                db_port = settings.DATABASES['default']['PORT']
                db_host = settings.DATABASES['default']['HOST']
                db_passwd = settings.DATABASES['default']['PASSWORD']

                helpers.patch_db(db_name, db_user, db_port, db_host, db_passwd, settings.MONITORING_ENABLED)
            except:
                traceback.print_exc()

            try:
                # Deactivate GeoNode Signals
                print "Deactivating GeoNode Signals..."
                designals()
                print "...done!"

                # Flush DB
                try:
                    db_name = settings.DATABASES['default']['NAME']
                    db_user = settings.DATABASES['default']['USER']
                    db_port = settings.DATABASES['default']['PORT']
                    db_host = settings.DATABASES['default']['HOST']
                    db_passwd = settings.DATABASES['default']['PASSWORD']

                    helpers.flush_db(db_name, db_user, db_port, db_host, db_passwd)
                except:
                    try:
                        call_command('flush', interactive=False, load_initial_data=False)
                    except:
                        traceback.print_exc()
                        raise

                # Restore Fixtures
                for app_name, dump_name in zip(config.app_names, config.dump_names):
                    fixture_file = os.path.join(target_folder, dump_name+'.json')

                    print "Deserializing "+fixture_file
                    try:
                        call_command('loaddata', fixture_file, app_label=app_name)
                    except:
                        traceback.print_exc()
                        print "WARNING: No valid fixture data found for '"+dump_name+"'."
                        # helpers.load_fixture(app_name, fixture_file)
                        raise

                # Restore Media Root
                try:
                    shutil.rmtree(media_root)
                except:
                    pass

                if not os.path.exists(media_root):
                    os.makedirs(media_root)

                helpers.copy_tree(media_folder, media_root)
                helpers.chmod_tree(media_root)
                print "Media Files Restored into '"+media_root+"'."

                # Restore Static Root
                try:
                    shutil.rmtree(static_root)
                except:
                    pass

                if not os.path.exists(static_root):
                    os.makedirs(static_root)

                helpers.copy_tree(static_folder, static_root)
                helpers.chmod_tree(static_root)
                print "Static Root Restored into '"+static_root+"'."

                # Restore Static Root
                try:
                    shutil.rmtree(static_root)
                except:
                    pass

                if not os.path.exists(static_root):
                    os.makedirs(static_root)

                helpers.copy_tree(static_folder, static_root)
                helpers.chmod_tree(static_root)
                print "Static Root Restored into '"+static_root+"'."

                # Restore Static Folders
                for static_files_folder in static_folders:
                    try:
                        shutil.rmtree(static_files_folder)
                    except:
                        pass

                    if not os.path.exists(static_files_folder):
                        os.makedirs(static_files_folder)

                    helpers.copy_tree(os.path.join(static_files_folders,
                                                   os.path.basename(os.path.normpath(static_files_folder))),
                                      static_files_folder)
                    helpers.chmod_tree(static_files_folder)
                    print "Static Files Restored into '"+static_files_folder+"'."

                # Restore Template Folders
                for template_files_folder in template_folders:
                    try:
                        shutil.rmtree(template_files_folder)
                    except:
                        pass

                    if not os.path.exists(template_files_folder):
                        os.makedirs(template_files_folder)

                    helpers.copy_tree(os.path.join(template_files_folders,
                                                   os.path.basename(os.path.normpath(template_files_folder))),
                                      template_files_folder)
                    helpers.chmod_tree(template_files_folder)
                    print "Template Files Restored into '"+template_files_folder+"'."

                # Restore Locale Folders
                for locale_files_folder in locale_folders:
                    try:
                        shutil.rmtree(locale_files_folder)
                    except:
                        pass

                    if not os.path.exists(locale_files_folder):
                        os.makedirs(locale_files_folder)

                    helpers.copy_tree(os.path.join(locale_files_folders,
                                                   os.path.basename(os.path.normpath(locale_files_folder))),
                                      locale_files_folder)
                    helpers.chmod_tree(locale_files_folder)
                    print "Locale Files Restored into '"+locale_files_folder+"'."

                call_command('collectstatic', interactive=False)

                # Cleanup DB
                try:
                    db_name = settings.DATABASES['default']['NAME']
                    db_user = settings.DATABASES['default']['USER']
                    db_port = settings.DATABASES['default']['PORT']
                    db_host = settings.DATABASES['default']['HOST']
                    db_passwd = settings.DATABASES['default']['PASSWORD']

                    helpers.cleanup_db(db_name, db_user, db_port, db_host, db_passwd)
                except:
                    traceback.print_exc()

                return str(target_folder)

            finally:
                # Reactivate GeoNode Signals
                print "Reactivating GeoNode Signals..."
                resignals()
                print "...done!"

                call_command('migrate', interactive=False, load_initial_data=False, fake=True)

                print "HINT: If you migrated from another site, do not forget to run the command 'migrate_baseurl' to fix Links"
                print " e.g.:  DJANGO_SETTINGS_MODULE=my_geonode.settings python manage.py migrate_baseurl --source-address=my-host-dev.geonode.org --target-address=my-host-prod.geonode.org"
                print "Restore finished. Please find restored files and dumps into:"
