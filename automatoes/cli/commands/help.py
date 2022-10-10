# -*- coding: UTF-8 -*-
#
# Copyright 2019-2022 Flávio Gonçalves Garcia
# Copyright 2016-2017 Veeti Paananen under MIT License
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ...cli import AutomatoesCliContext, pass_context
import click


@click.command(short_help="Show the list of commands")
@pass_context
def commands(ctx: AutomatoesCliContext):
    rv = []
    groups = []
    for source in ctx.context.loader.sources:
        for key, item in source.__dict__.items():
            if isinstance(item, click.Command):
                if isinstance(item, click.Group):
                    groups.append(item)
                rv.append(item.name)
    for group in groups:
        for key, item in group.commands.items():
            if item.name in rv:
                rv.remove(item.name)
    rv.sort()

    print(rv)
    print(groups)

    print("Test cli1 command")


@click.command(name="help", short_help="Show the help about a command")
def _help():
    print("Test cli1 command")
