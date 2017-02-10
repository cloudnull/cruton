# Copyright 2017, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# (c) 2017, Kevin Carter <kevin.carter@rackspace.com>


class DriverBase(object):
    def __init__(self):
        raise NotImplemented()

    def get_data(self, data_type=None, filters=None, traverse=False):
        """Return data from the backend data store.

        :param data_type: Table or key to work from when retrieving data.
        :param filters: Any filters used to return the data in a more concise way.
        :param traverse: If data has children return all children.
        :return:
        """
        raise NotImplemented()

    def put_data(self, data_type=None, data=None):
        """ Add data to a given data_type within a backend store.

        :param data_type: Type of data to interact with.
        :param data: data insert object.
        :return:
        """
        raise NotImplemented()
