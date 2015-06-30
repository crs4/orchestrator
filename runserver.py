# -*- coding:utf-8 -*-

# Copyright 2015 CRS4
# All Rights Reserved.
#
#    Licensed under the GNU General Public License, version 2 (the "License");
#    you may not use this file except in compliance with the License. You may
#    obtain a copy of the License at
#
#         http://www.gnu.org/licenses/gpl-2.0.html
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
    runserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: |copy| 2015 by CRS4.
    :license: gpl-2, see License for more details.

    Entry point to execute manually the flask application

    >> python runserver.py

"""

import argparse
from dispatcher import app


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port', '-p', default = app.config['PORT'], type=int,
        help='port on which to run server')
    parser.add_argument(
    	'--host', '-n', default = app.config['HOST'],
    	help='where to run server')
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug = app.config.get('DEBUG', True) )
