# AWS Tools

## Requirements

Please use Python 3 and install the dependencies:

```shell
pip install -r requirements.txt
```


## ECS Healthy

Checks the matching tasks are HEALTHY and the services reached a steady state.

Features:

- The services are considered healthy if the last registered event contains
    the text `has reached a steady state`.
- The tasks are considered healthy if the Health Status is `HEALTHY`.
- When all matched services and tasks are considered healthy, the script will
    pause until any key is pressed, otherwise, when at least one resource is 
    not healthy, the script will loop waiting 5 seconds until all resources 
    are considered healthy.
- Information displayed per each service: 
    - Launch Type
    - Service Name
    - Status
    - Running count versus desired count
    - Last event registered
- Information displayed per each task:
    - Task ARN
    - Container Image
    - Health Status

Syntax:

```shell
python ecs_healthy.py AWS_PROFILE CLUSTER_FILTER SERVICE_FILTER
```

- `AWS_PROFILE`: Required. The AWS profile name which must be able to:
    - List clusters, services and tasks.
    - Describe services and tasks.

- `CLUSTER_FILTER` and `SERVICE_FILTER`: Are used to match clusters and 
    services respectively. The matching uses the ARN of the resource and
    applies a _contains_ condition.
