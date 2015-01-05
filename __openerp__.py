# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2015 litnimax
#    (False).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'GTD',
    'version': '0.1',
    'author': 'litnimax',
    'maintainer': 'False',
    'website': 'False',
    'license': 'AGPL-3',
    'category': 'Project',
    'summary': 'GTD',
    'description': """
GTD

* Module exported by the prototype module for version 8.0.
* If you have any questions, please contact Savoir-faire Linux \
(support@savoirfairelinux.com)
""",
    'depends': [
        'web',
        'mail'
        ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'views/gtd.xml',
        'views/task.xml',
        ],
    'demo': [
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
