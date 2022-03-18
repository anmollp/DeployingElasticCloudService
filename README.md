# DeployingElasticCloudService

1. Set up your **aws access** and **secret keys** in your bash profile or bash rc file so that they can be used for authentication purposes.
2. Use the **instance id** from **Homework2** for creating an image.
3. Use the **print_http** library for printing request and response in a **messages.txt** file. The library is provided as a file **print_http.py**.
4. A **VPC** has to be set up before proceeding to create an elastic cloud service, in your aws account.
5. Screenshots of the aws monthly bills for February and March are attached.
6. Use **deploy.py** script to automate the whole deployment of an elastic cloud service.
7. **deploy.py** takes an argument called **Average CPU Utilization** (value between 0 and 1) that needs to be passed when calling the script as shown below:

      > ``python deploy.py 0.3``
8. Finally the output provides a **load balancer url** to connect to the service.

## List of libraries required to install/use before running script:
1. requests_aws4auth
2. xml
3. requests
4. print_http
