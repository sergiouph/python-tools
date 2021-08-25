from typing import List, Dict
import time
import boto3
import sys


def main():
    if len(sys.argv) != 4:
        print(f'Syntax: {sys.argv[0]} AWS_PROFILE CLUSTER_FILTER SERVICE_FILTER')
        return

    profile_name = sys.argv[1]
    cluster_filter = sys.argv[2]
    service_filter = sys.argv[3]

    session = boto3.session.Session(profile_name=profile_name)
    client = session.client('ecs')

    while True:
        try:
            print('-' * 80)
            print(f'  AWS profile     :  {profile_name}')
            print(f'  Cluster filter  :  {cluster_filter}')
            print(f'  Service filter  :  {service_filter}')
            print('-' * 80)

            healthy = True

            cluster_services = fetch_cluster_and_services(
                client, cluster_filter, service_filter)

            for cluster, services in cluster_services.items():
                result = check_services(client, cluster, services)

                healthy = result and healthy

            if healthy:
                print('')
                print('✅ Everything is HEALTHY!')
                print('')
                input('Press any key or CTRL+C... ')
            else:
                print('')
                print('❌ Not healthy!')
                print('')

                for i in reversed(range(5)):
                    print(f'Retrying in {i+1}s...')
                    time.sleep(1)
        except KeyboardInterrupt:
            print('')
            print('Bye!')
            print('')
            break


def fetch_cluster_and_services(
        client,
        cluster_filter: str,
        service_filter: str) -> Dict[str, List[str]]:
    cluster_services = {}

    for cluster_arn in collect({}, 'clusterArns', client.list_clusters):
        services = []

        if cluster_filter in cluster_arn:
            service_arns = [
                service_arn
                for service_arn in collect(
                    request0={'cluster': cluster_arn},
                    field_key='serviceArns',
                    action=client.list_services)
                if service_filter in service_arn
            ]

            if len(service_arns) > 0:
                services.extend(service_arns)

        if len(services) > 0:
            cluster_services[cluster_arn] = services

    return cluster_services


def check_services(client, cluster_arn: str, service_arns: List[str]) -> bool:
    healthy = True
    response = client.describe_services(
        cluster=cluster_arn,
        services=service_arns)

    for service in response['services']:
        service_name = service['serviceName']
        launch_type = service['launchType']
        events = service['events']

        print(
            f'{launch_type} - {service_name} ['
            f'{service["status"]}, running {service["runningCount"]}/'
            f'{service["desiredCount"]}]')

        if len(events) > 0:
            last_event = events[0]
            event_msg = last_event['message']
            event_time = last_event['createdAt'].isoformat()
            print(f'\tLast Event: {event_msg} [{event_time}]')

            if 'has reached a steady state' not in event_msg:
                healthy = False

        task_arns = collect({
            'cluster': cluster_arn,
            'serviceName': service_name,
        }, 'taskArns', client.list_tasks)

        response = client.describe_tasks(
            cluster=cluster_arn,
            tasks=task_arns,
        )

        for task in response['tasks']:
            task_arn = task['taskArn']

            print(f'\tTask: {task_arn}')

            for container in task['containers']:
                container_image = container['image']
                container_health_status = container['healthStatus']
                print(f'\t\tContainer: {container_image} [{container_health_status}]')

                if container_health_status != 'HEALTHY':
                    healthy = False

    return healthy


def collect(request0: dict, field_key: str, action):
    result = []
    request = {**request0}

    while True:
        response = action(**request)

        result.extend(response[field_key])

        request['nextToken'] = response.get('nextToken')

        if not request.get('nextToken'):
            break

    return result


if __name__ == '__main__':
    main()
