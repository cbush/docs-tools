# Copyright 2015 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import libgiza.task

import giza.tools.files
import giza.tools.transformation

logger = logging.getLogger('giza.content.system')


def migration_tasks(conf):
    tasks = []

    migration_spec_files = conf.system.files.get_configs('migration')

    for migration in conf.system.files.data.migrations:
        copy_job = libgiza.task.Task(job=giza.tools.file.copy_if_needed,
                                     args=(migration.source, migration.target),
                                     target=migration.target,
                                     dependency=migration.source)

        if migration.truncate is not None:
            # this only needs to run if the parent task runs
            copy_job.finalizers = libgiza.task.Task(job=giza.tools.transformation.truncate_file,
                                                    args=(migration.target,
                                                          migration.truncate.start_after,
                                                          migration.truncate.end_before),
                                                    target=migration.target,
                                                    dependency=migration.source)

        if migration.transform is not None:
            # causes needs_rebuild() to be always true, this must always run
            copy_job.dependency = None
            copy_job.job = giza.tools.file.copy_always

            regexes = [(t.regex, t.replacement) for t in migration.transform]
            transforms = giza.tools.transformation.process_page_task(fn=migration.target,
                                                                     output_fn=migration.target,
                                                                     regex=regexes,
                                                                     builder='migration',
                                                                     copy='ifNeeded')
            copy_job.finalizers = transforms

        if migration.append is not None:
            # causes needs_rebuild() to be always true, this must always run
            copy_job.dependency = None
            copy_job.job = giza.tools.file.copy_always
            copy_job.finalizers = libgiza.task.Task(job=giza.tools.transformation.append_to_file,
                                                    args=(migration.target, migration.append),
                                                    target=migration.target,
                                                    dependency=migration_spec_files)

        tasks.append(copy_job)

    logger.info('created {0} file migration tasks'.format(len(tasks)))
    return tasks
