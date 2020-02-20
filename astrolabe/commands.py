# Copyright 2020-present MongoDB, Inc.
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

from atlasclient import AtlasApiError


def get_one_organization_by_name(*, client, organization_name):
    all_orgs = client.orgs.get().data
    for org in all_orgs.results:
        if org.name == organization_name:
            return org
    raise AtlasApiError('Resource not found.')


def ensure_project(*, client, group_name, organization_id):
    try:
        return client.groups.post(
            name=group_name, orgId=organization_id).data
    except AtlasApiError as exc:
        if exc.error_code == 'GROUP_ALREADY_EXISTS':
            return client.groups.byName[group_name].get().data
        else:
            raise


def ensure_admin_user(*, client, group_id, username, password):
    user_details = {
        "groupId": group_id,
        "databaseName": "admin",
        "roles": [{
            "databaseName": "admin",
            "roleName": "atlasAdmin"}],
        "username": username,
        "password": password}

    try:
        return client.groups[group_id].databaseUsers.post(**user_details).data
    except AtlasApiError as exc:
        if exc.error_code == "USER_ALREADY_EXISTS":
            username = user_details.pop("username")
            return client.groups[group_id].databaseUsers.admin[username].patch(
                **user_details).data
        else:
            raise


def ensure_connect_from_anywhere(*, client, group_id,):
    ip_details_list = [{"cidrBlock": "0.0.0.0/0"}]
    client.groups[group_id].whitelist.post(json=ip_details_list)
