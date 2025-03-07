# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from argcomplete.completers import FilesCompleter
from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (get_location_type,
                                                file_type,
                                                get_resource_name_completion_list,
                                                get_enum_type,
                                                get_three_state_flag)
from azure.mgmt.iothub.models import IotHubSku
from azure.mgmt.iothubprovisioningservices.models import (IotDpsSku,
                                                          AllocationPolicy,
                                                          AccessRightsDescription)
from azure.cli.command_modules.iot.shared import (EndpointType,
                                                  RouteSourceType,
                                                  EncodingFormat,
                                                  RenewKeyType,
                                                  UserRole)
from .custom import KeyType, SimpleAccessRights
from ._validators import (validate_policy_permissions,
                          validate_retention_days,
                          validate_fileupload_notification_max_delivery_count,
                          validate_fileupload_notification_ttl,
                          validate_fileupload_sas_ttl,
                          validate_feedback_ttl,
                          validate_feedback_lock_duration,
                          validate_feedback_max_delivery_count,
                          validate_c2d_max_delivery_count,
                          validate_c2d_ttl)


hub_name_type = CLIArgumentType(
    completer=get_resource_name_completion_list('Microsoft.Devices/IotHubs'),
    help='IoT Hub name.')

dps_name_type = CLIArgumentType(
    options_list=['--dps-name'],
    completer=get_resource_name_completion_list('Microsoft.Devices/ProvisioningServices'),
    help='IoT Provisioning Service name')


def load_arguments(self, _):  # pylint: disable=too-many-statements
    # Arguments for IoT DPS
    with self.argument_context('iot dps') as c:
        c.argument('dps_name', dps_name_type, options_list=['--name', '-n'], id_part='name')

    with self.argument_context('iot dps create') as c:
        c.argument('location', get_location_type(self.cli_ctx),
                   help='Location of your IoT Provisioning Service. Default is the location of target resource group.')
        c.argument('sku', arg_type=get_enum_type(IotDpsSku),
                   help='Pricing tier for the IoT provisioning service.')
        c.argument('unit', help='Units in your IoT Provisioning Service.', type=int)

    for subgroup in ['access-policy', 'linked-hub', 'certificate']:
        with self.argument_context('iot dps {}'.format(subgroup)) as c:
            c.argument('dps_name', options_list=['--dps-name'], id_part=None)

    with self.argument_context('iot dps access-policy') as c:
        c.argument('access_policy_name', options_list=['--access-policy-name', '--name', '-n'],
                   help='A friendly name for DPS access policy.')

    with self.argument_context('iot dps access-policy create') as c:
        c.argument('rights', options_list=['--rights', '-r'], nargs='+',
                   arg_type=get_enum_type(AccessRightsDescription),
                   help='Access rights for the IoT provisioning service. Use space-separated list for multiple rights.')
        c.argument('primary_key', help='Primary SAS key value.')
        c.argument('secondary_key', help='Secondary SAS key value.')

    with self.argument_context('iot dps access-policy update') as c:
        c.argument('rights', options_list=['--rights', '-r'], nargs='+',
                   arg_type=get_enum_type(AccessRightsDescription),
                   help='Access rights for the IoT provisioning service. Use space-separated list for multiple rights.')
        c.argument('primary_key', help='Primary SAS key value.')
        c.argument('secondary_key', help='Secondary SAS key value.')

    with self.argument_context('iot dps linked-hub') as c:
        c.argument('linked_hub', options_list=['--linked-hub'], help='Host name of linked IoT Hub.')

    with self.argument_context('iot dps linked-hub create') as c:
        c.argument('connection_string', help='Connection string of the IoT hub.')
        c.argument('location', get_location_type(self.cli_ctx),
                   help='Location of the IoT hub.')
        c.argument('apply_allocation_policy',
                   help='A boolean indicating whether to apply allocation policy to the IoT hub.',
                   arg_type=get_three_state_flag())
        c.argument('allocation_weight', help='Allocation weight of the IoT hub.')

    with self.argument_context('iot dps linked-hub update') as c:
        c.argument('apply_allocation_policy',
                   help='A boolean indicating whether to apply allocation policy to the Iot hub.',
                   arg_type=get_three_state_flag())
        c.argument('allocation_weight', help='Allocation weight of the IoT hub.')

    with self.argument_context('iot dps allocation-policy update') as c:
        c.argument('allocation_policy', options_list=['--policy', '-p'], arg_type=get_enum_type(AllocationPolicy),
                   help='Allocation policy for the IoT provisioning service.')

    with self.argument_context('iot dps certificate') as c:
        c.argument('certificate_path', options_list=['--path', '-p'], type=file_type,
                   completer=FilesCompleter([".cer", ".pem"]), help='The path to the file containing the certificate.')
        c.argument('certificate_name', options_list=['--certificate-name', '--name', '-n'],
                   help='A friendly name for the certificate.')
        c.argument('etag', options_list=['--etag', '-e'], help='Entity Tag (etag) of the object.')

    # Arguments for IoT Hub
    with self.argument_context('iot hub') as c:
        c.argument('hub_name', hub_name_type, options_list=['--name', '-n'], id_part='name')
        c.argument('etag', options_list=['--etag', '-e'], help='Entity Tag (etag) of the object.')
        c.argument('sku', arg_type=get_enum_type(IotHubSku),
                   help='Pricing tier for Azure IoT Hub. Default value is F1, which is free. '
                        'Note that only one free IoT hub instance is allowed in each '
                        'subscription. Exception will be thrown if free instances exceed one.')
        c.argument('unit', help='Units in your IoT Hub.', type=int)
        c.argument('partition_count',
                   help='The number of partitions of the backing Event Hub for device-to-cloud messages.', type=int)
        c.argument('retention_day', options_list=['--retention-day', '--rd'],
                   type=int, validator=validate_retention_days,
                   help='Specifies how long this IoT hub will maintain device-to-cloud events, between 1 and 7 days.')
        c.argument('c2d_ttl', options_list=['--c2d-ttl', '--ct'],
                   type=int, validator=validate_c2d_ttl,
                   help='The amount of time a message is available for the device to consume before it is expired'
                        ' by IoT Hub, between 1 and 48 hours.')
        c.argument('c2d_max_delivery_count', options_list=['--c2d-max-delivery-count', '--cdd'],
                   type=int, validator=validate_c2d_max_delivery_count,
                   help='The number of times the IoT hub will attempt to deliver a cloud-to-device'
                        ' message to a device, between 1 and 100.')
        c.argument('feedback_ttl', options_list=['--feedback-ttl', '--ft'],
                   type=int, validator=validate_feedback_ttl,
                   help='The period of time for which the IoT hub will maintain the feedback for expiration'
                        ' or delivery of cloud-to-device messages, between 1 and 48 hours.')
        c.argument('feedback_lock_duration', options_list=['--feedback-lock-duration', '--fld'],
                   type=int, validator=validate_feedback_lock_duration,
                   help='The lock duration for the feedback queue, between 5 and 300 seconds.')
        c.argument('feedback_max_delivery_count', options_list=['--feedback-max-delivery-count', '--fd'],
                   type=int, validator=validate_feedback_max_delivery_count,
                   help='The number of times the IoT hub attempts to'
                        ' deliver a message on the feedback queue, between 1 and 100.')
        c.argument('enable_fileupload_notifications', options_list=['--fileupload-notifications', '--fn'],
                   arg_type=get_three_state_flag(),
                   help='A boolean indicating whether to log information about uploaded files to the'
                        ' messages/servicebound/filenotifications IoT Hub endpoint.')
        c.argument('fileupload_notification_max_delivery_count', type=int,
                   options_list=['--fileupload-notification-max-delivery-count', '--fnd'],
                   validator=validate_fileupload_notification_max_delivery_count,
                   help='The number of times the IoT hub will attempt to deliver a file notification message,'
                        ' between 1 and 100.')
        c.argument('fileupload_notification_ttl', options_list=['--fileupload-notification-ttl', '--fnt'],
                   type=int, validator=validate_fileupload_notification_ttl,
                   help='The amount of time a file upload notification is available for the service to'
                        ' consume before it is expired by IoT Hub, between 1 and 48 hours.')
        c.argument('fileupload_storage_connectionstring',
                   options_list=['--fileupload-storage-connectionstring', '--fcs'],
                   help='The connection string for the Azure Storage account to which files are uploaded.')
        c.argument('fileupload_storage_container_name',
                   options_list=['--fileupload-storage-container-name', '--fc'],
                   help='The name of the root container where you upload files. The container need not exist but'
                        ' should be creatable using the connectionString specified.')
        c.argument('fileupload_sas_ttl', options_list=['--fileupload-sas-ttl', '--fst'],
                   type=int, validator=validate_fileupload_sas_ttl,
                   help='The amount of time a SAS URI generated by IoT Hub is valid before it expires,'
                        ' between 1 and 24 hours.')

    for subgroup in ['consumer-group', 'policy', 'job', 'certificate', 'routing-endpoint', 'route']:
        with self.argument_context('iot hub {}'.format(subgroup)) as c:
            c.argument('hub_name', options_list=['--hub-name'])

    with self.argument_context('iot hub route') as c:
        c.argument('route_name', options_list=['--route-name', '--name', '-n'], help='Name of the Route.')
        c.argument('endpoint_name', options_list=['--endpoint-name', '--endpoint', '--en'],
                   help='Name of the routing endpoint.')
        c.argument('condition', options_list=['--condition', '-c'],
                   help='Condition that is evaluated to apply the routing rule.')
        c.argument('enabled', options_list=['--enabled', '-e'], arg_type=get_three_state_flag(),
                   help='A boolean indicating whether to enable route to the Iot hub.')
        c.argument('source_type', arg_type=get_enum_type(RouteSourceType),
                   options_list=['--source-type', '--type', '--source', '-s'], help='Source of the route.')

    with self.argument_context('iot hub route test') as c:
        c.argument('body', options_list=['--body', '-b'], help='Body of the route message.')
        c.argument('app_properties', options_list=['--app-properties', '--ap'],
                   help='App properties of the route message.')
        c.argument('system_properties', options_list=['--system-properties', '--sp'],
                   help='System properties of the route message.')

    with self.argument_context('iot hub routing-endpoint') as c:
        c.argument('endpoint_name', options_list=['--endpoint-name', '--name', '-n'],
                   help='Name of the Routing Endpoint.')
        c.argument('endpoint_resource_group', options_list=['--endpoint-resource-group', '--erg', '-r'],
                   help='Resource group of the Endpoint resoure.')
        c.argument('endpoint_subscription_id', options_list=['--endpoint-subscription-id', '-s'],
                   help='SubscriptionId of the Endpoint resource.')
        c.argument('connection_string', options_list=['--connection-string', '-c'],
                   help='Connection string of the Routing Endpoint.')
        c.argument('container_name', options_list=['--container-name', '--container'],
                   help='Name of the storage container.')
        c.argument('endpoint_type', arg_type=get_enum_type(EndpointType),
                   options_list=['--endpoint-type', '--type', '-t'], help='Type of the Routing Endpoint.')
        c.argument('encoding', options_list=['--encoding'], arg_type=get_enum_type(EncodingFormat),
                   help='Encoding format for the container. The default is AVRO. '
                        'Note that this field is applicable only for blob container endpoints.')

    with self.argument_context('iot hub routing-endpoint create') as c:
        c.argument('batch_frequency', options_list=['--batch-frequency', '-b'], type=int,
                   help='Request batch frequency in seconds. The maximum amount of time that can elapse before data is'
                        ' written to a blob, between 60 and 720 seconds.')
        c.argument('chunk_size_window', options_list=['--chunk-size', '-w'], type=int,
                   help='Request chunk size in megabytes(MB). The maximum size of blobs, between 10 and 500 MB.')
        c.argument('file_name_format', options_list=['--file-name-format', '--ff'],
                   help='File name format for the blob. The file name format must contain {iothub},'
                        ' {partition}, {YYYY}, {MM}, {DD}, {HH} and {mm} fields. All parameters are'
                        ' mandatory but can be reordered with or without delimiters.')

    with self.argument_context('iot hub certificate') as c:
        c.argument('certificate_path', options_list=['--path', '-p'], type=file_type,
                   completer=FilesCompleter([".cer", ".pem"]), help='The path to the file containing the certificate.')
        c.argument('certificate_name', options_list=['--name', '-n'], help='A friendly name for the certificate.')

    with self.argument_context('iot hub consumer-group') as c:
        c.argument('consumer_group_name', options_list=['--name', '-n'], id_part='child_name_2',
                   help='Event hub consumer group name.')
        c.argument('event_hub_name', id_part='child_name_1', help='Event hub endpoint name.')

    with self.argument_context('iot hub policy') as c:
        c.argument('policy_name', options_list=['--name', '-n'], id_part='child_name_1',
                   help='Shared access policy name.')
        permission_values = ', '.join([x.value for x in SimpleAccessRights])
        c.argument('permissions', nargs='*', validator=validate_policy_permissions, type=str.lower,
                   help='Permissions of shared access policy. Use space-separated list for multiple permissions. '
                        'Possible values: {}'.format(permission_values))

    with self.argument_context('iot hub policy renew-key') as c:
        c.argument('regenerate_key', options_list=['--renew-key', '--rk'], arg_type=get_enum_type(RenewKeyType),
                   help='Regenerate keys')

    with self.argument_context('iot hub job') as c:
        c.argument('job_id', id_part='child_name_1', help='Job Id.')

    with self.argument_context('iot hub create') as c:
        c.argument('hub_name', completer=None)
        c.argument('location', get_location_type(self.cli_ctx),
                   help='Location of your IoT Hub. Default is the location of target resource group.')

    with self.argument_context('iot hub show-connection-string') as c:
        c.argument('show_all', options_list=['--all'], help='Allow to show all shared access policies.')
        c.argument('hub_name', options_list=['--hub-name', '--name', '-n'])
        c.argument('policy_name', help='Shared access policy to use.')
        c.argument('key_type', arg_type=get_enum_type(KeyType), options_list=['--key'], help='The key to use.')

    with self.argument_context('iot hub manual-failover') as c:
        c.argument('failover_region', options_list=['--failover-region', '--fr'], help='The region that the IoT hub'
                   'fails over to. Must be the paired region to the current IoT hub region.')

    # Arguments for Message Enrichments
    with self.argument_context('iot hub message-enrichment') as c:
        c.argument('key', options_list=['--key', '-k'], help='The enrichment\'s key.')
        c.argument('value', options_list=['--value', '-v'], help='The enrichment\'s value.')
        c.argument('endpoints', options_list=['--endpoints', '-e'], nargs='*',
                   help='Endpoint(s) to apply enrichments to. Use a space-separated list for multiple endpoints.')

    # Arguments for IoT Digital Twin
    with self.argument_context('iot pnp') as c:
        c.argument('repo_endpoint', options_list=['--endpoint', '-e'], help='IoT Plug and Play endpoint.')
        c.argument('repo_id', options_list=['--repo-id', '-r'], help='IoT Plug and Play repository Id.')

    with self.argument_context('iot pnp repository') as c:
        c.argument('repo_name', options_list=['--name', '-n'], help='IoT Plug and Play repository Name.')

    with self.argument_context('iot pnp repository get-provision-status') as c:
        c.argument('track_id', options_list=['--provisioning-State', '-s'],
                   help='Provisioning state of an IoT Plug and Play repository.')

    with self.argument_context('iot pnp key') as c:
        c.argument('key_id', options_list=['--key-id', '-k'],
                   help='Access key for the given IoT Plug and Play repository.')
        c.argument('user_role', options_list=['--role'], arg_type=get_enum_type(UserRole),
                   help='User role of the access key for the given IoT Plug and Play repository.')
