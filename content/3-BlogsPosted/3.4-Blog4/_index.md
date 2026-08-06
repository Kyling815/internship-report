---
title: "Blog 4"
date: 2026-07-29
weight: 4
chapter: false
pre: " <b> 3.4. </b> "
---

# AWS Networking Advanced: 3 Techniques for Building an Enterprise-Grade VPC

## Introduction

A basic Amazon VPC architecture consisting of public subnets, private subnets, and a NAT Gateway is a suitable foundation for deploying applications on AWS. This architecture separates resources that require direct Internet access from internal components such as application servers, databases, and caches.

However, when a system expands to include Development, Staging, and Production environments or is divided across multiple microservices and VPCs, the basic architecture may begin to present three major limitations:

- Increasing NAT Gateway costs caused by frequent access from private subnets to Amazon S3, Amazon DynamoDB, and other AWS services.
- A potential single point of failure when all outbound traffic depends on one NAT Gateway in one Availability Zone.
- Complex network management when many VPCs are connected through a full-mesh VPC Peering model.

This article presents three techniques for upgrading a VPC architecture for enterprise environments: VPC Endpoints, Multi-AZ networking, and AWS Transit Gateway.


## 1. Reducing Costs and Improving Security with VPC Endpoints

### The NAT Gateway Traffic Problem

EC2 instances, containers, and application servers running in private subnets usually do not have public IP addresses. When these resources need to access Amazon S3, DynamoDB, or other AWS services, their traffic may pass through a NAT Gateway.

A basic traffic flow may look like this:

```text
Private Subnet
      |
      v
NAT Gateway
      |
      v
AWS Public Service Endpoint
```

This design may introduce hourly NAT Gateway charges and data-processing costs. Traffic may also pass through a public service endpoint even though both the application and destination service operate within AWS infrastructure.

### Gateway Endpoints

Gateway Endpoints are available for two primary services:

- Amazon S3.
- Amazon DynamoDB.

After a Gateway Endpoint is created and associated with the route tables of private subnets, traffic to S3 or DynamoDB can travel directly through the AWS network without using a NAT Gateway.

The updated traffic flow can be represented as follows:

```text
Private Subnet
      |
      v
VPC Gateway Endpoint
      |
      v
Amazon S3 or Amazon DynamoDB
```

Gateway Endpoints provide several benefits:

- A NAT Gateway is no longer required for S3 and DynamoDB traffic.
- Traffic remains within the AWS network.
- NAT Gateway data-processing costs can be reduced.
- Access can be controlled through endpoint policies.
- Workloads become less dependent on outbound Internet connectivity.

Gateway Endpoints for S3 and DynamoDB do not have hourly endpoint charges, which makes them one of the first options to consider when optimizing network costs.

### Interface Endpoints and AWS PrivateLink

For AWS services that do not support Gateway Endpoints, an Interface Endpoint can be used.

An Interface Endpoint creates Elastic Network Interfaces inside selected subnets and assigns private IP addresses to them. Applications can then access the target AWS service through private IP addresses or private DNS without using the public Internet.

Services commonly accessed through Interface Endpoints include:

- Amazon CloudWatch.
- AWS Secrets Manager.
- Amazon ECR.
- AWS Systems Manager.
- AWS Key Management Service.
- Amazon Kinesis.

Interface Endpoints use AWS PrivateLink to keep service traffic inside the AWS network.

Compared with NAT Gateway access, this design can:

- Reduce outbound Internet traffic.
- Control access through Security Groups.
- Reduce the attack surface.
- Support a clearer private-networking model.
- Allow private workloads to access AWS services through private IP addresses.

Interface Endpoints still have hourly and data-processing charges. Their cost should therefore be compared with NAT Gateway costs based on the actual traffic patterns of the system.

## 2. Deploying Across Multiple Availability Zones and Avoiding Unnecessary Cross-AZ Costs

### Why Multiple Availability Zones Matter

An Availability Zone can experience an independent failure. If all application servers, databases, and outbound networking resources are placed in one AZ, the entire system may become unavailable when that AZ is affected.

For higher availability, production architectures are commonly deployed across at least two Availability Zones.

For example:

```text
Availability Zone A
- Public Subnet A
- Private Subnet A
- NAT Gateway A
- Application instances A

Availability Zone B
- Public Subnet B
- Private Subnet B
- NAT Gateway B
- Application instances B
```

In this model, each Availability Zone has an independent outbound path. If one AZ becomes unavailable, workloads in the remaining AZ can continue using the NAT Gateway and resources available in that AZ.

### Avoiding a Single Point of Failure

If the system uses only one NAT Gateway in AZ-A, workloads in AZ-B must send their outbound traffic across Availability Zone boundaries before reaching the gateway.

This creates two issues:

1. The NAT Gateway in AZ-A becomes a shared point of dependency.
2. Traffic from AZ-B to AZ-A may generate Cross-AZ data-transfer charges.

A more resilient architecture deploys one NAT Gateway in every active Availability Zone. Each private subnet route table is configured to use the NAT Gateway located in the same AZ.

For example:

```text
Private Subnet A -> NAT Gateway A
Private Subnet B -> NAT Gateway B
```

If AZ-A becomes unavailable, resources in AZ-B still have an independent outbound path and do not depend on NAT Gateway A.

### AZ-Aware Routing

AZ-aware routing prioritizes communication between workloads and dependencies located in the same Availability Zone.

Examples include:

- An application instance in AZ-A using NAT Gateway A.
- A workload in AZ-B connecting to a cache node in AZ-B.
- A load balancer distributing requests to suitable targets.
- Database replicas or cache nodes being distributed across multiple AZs.
- Service discovery preferring endpoints located closer to the workload when supported.

This design can:

- Reduce unnecessary Cross-AZ traffic.
- Reduce network latency.
- Limit inter-AZ data-transfer costs.
- Allow each AZ to operate more independently.

However, AZ locality must still be balanced with High Availability requirements. An application should not depend entirely on one local resource if that dependency does not provide a failover mechanism.

## 3. Managing Multi-VPC Connectivity with AWS Transit Gateway

### Limitations of VPC Peering

VPC Peering works well when only a small number of VPCs need to communicate. Two VPCs can be connected directly and exchange traffic through private IP addresses.

However, VPC Peering does not support transitive routing.

For example:

```text
VPC-A <-> VPC-B
VPC-B <-> VPC-C
```

The fact that VPC-A connects to VPC-B and VPC-B connects to VPC-C does not automatically allow VPC-A to communicate with VPC-C.

When many VPCs require direct connections, the number of VPC Peering connections can grow according to the following formula:

```text
N(N - 1) / 2
```

With 10 VPCs, a full-mesh design may require up to 45 peering connections.

At this scale, managing route tables, CIDR ranges, Security Groups, and network policies becomes increasingly difficult. Adding one new VPC may also require multiple new connections and route-table updates.

### Transit Gateway as a Cloud Router

AWS Transit Gateway acts as a centralized router for multiple VPCs and external networks.

Resources that can connect to a Transit Gateway include:

- Amazon VPCs.
- Site-to-Site VPN connections.
- AWS Direct Connect through a Direct Connect Gateway.
- VPCs from multiple AWS accounts.
- Development, Staging, and Production environments.
- Shared Services VPCs.
- On-Premises data center networks.

Instead of creating direct connections between every pair of VPCs, each VPC creates a single attachment to the Transit Gateway.

```text
             Development VPC
                    |
                    |
Shared VPC ---- Transit Gateway ---- Production VPC
                    |
                    |
             On-Premises Network
```

This hub-and-spoke model simplifies the network topology and centralizes routing management.

### Network Segmentation with Transit Gateway Route Tables

Transit Gateway can use multiple route tables to control which VPCs and networks are allowed to communicate.

For example:

- The Development VPC can access the Shared Services VPC.
- The Production VPC can access the Shared Services VPC.
- The Development VPC cannot directly access the Production VPC.
- The On-Premises Network can access only selected subnets.
- A Security VPC can inspect traffic before forwarding it to other VPCs.

This segmentation can:

- Reduce lateral movement between environments.
- Separate Development, Staging, and Production more clearly.
- Centralize network-policy management.
- Simplify the addition of new VPCs.
- Support multi-account architectures with AWS Organizations.

## Comparing Basic and Enterprise VPC Architectures

| Category | Basic Architecture | Enterprise Architecture |
|---|---|---|
| Access to S3 and DynamoDB | Through a NAT Gateway or public endpoint | Through a Gateway Endpoint |
| Access to other AWS services | Commonly through a NAT Gateway | Through Interface Endpoints and AWS PrivateLink when appropriate |
| High Availability | May depend on one NAT Gateway | Independent NAT Gateway in each Availability Zone |
| Cross-AZ traffic | May increase because of inefficient routing | Reduced through AZ-aware routing |
| Multi-VPC connectivity | VPC Peering configured manually between pairs | Centrally managed through Transit Gateway |
| Development and Production separation | Depends on multiple routes and peering connections | Controlled through Transit Gateway route tables |
| Scalability | Suitable for smaller systems | More suitable for multi-VPC and multi-account systems |
| Management | Simple initially but difficult to control at scale | More complex initially but easier to manage centrally |

## When Should Each Technique Be Used?

### Use VPC Endpoints when:

- Workloads in private subnets frequently access Amazon S3 or DynamoDB.
- Applications need to access AWS services without using the public Internet.
- NAT Gateway traffic and processing costs need to be reduced.
- The system has stronger data-security requirements.
- Access needs to be limited through endpoint policies.

### Use Multi-AZ NAT Gateways when:

- The system requires High Availability.
- Workloads operate across multiple Availability Zones.
- A single NAT Gateway should not become a single point of failure.
- Unnecessary Cross-AZ traffic should be reduced.
- Outbound connectivity must remain available when one AZ fails.

### Use AWS Transit Gateway when:

- The organization operates many VPCs or AWS accounts.
- On-Premises networks must connect to AWS.
- VPC Peering has become difficult to manage.
- Development, Staging, and Production require clear separation.
- Routing needs to be controlled from a central location.
- Shared Services or centralized Security Inspection architectures are required.

## Cost Considerations

An advanced network architecture does not mean that every component becomes less expensive.

Gateway Endpoints for S3 and DynamoDB can reduce traffic through NAT Gateways. However, Interface Endpoints, NAT Gateways, and Transit Gateway each have their own pricing models.

Before implementation, the architecture should consider:

- Total monthly data-transfer volume.
- AWS services frequently accessed by private workloads.
- Number of Availability Zones.
- Number of VPCs and Transit Gateway attachments.
- Frequency of Cross-AZ communication.
- Internet outbound traffic.
- Security and availability requirements.
- Operational cost and management complexity.

The objective is not simply to minimize cost. It is to find an appropriate balance between cost, security, performance, scalability, and High Availability.

## Conclusion

The combination of public subnets, private subnets, and a NAT Gateway provides a strong starting point for building applications on AWS. As the system grows across multiple environments, VPCs, or AWS accounts, the network architecture must also evolve.

Three important techniques are:

1. Use VPC Endpoints to keep AWS service traffic inside the AWS network and reduce dependence on NAT Gateways.
2. Deploy independent NAT Gateways across multiple Availability Zones to improve availability and reduce unnecessary Cross-AZ traffic.
3. Use AWS Transit Gateway to manage connectivity between multiple VPCs through a centralized model.

VPC optimization is not only a routing problem. It also involves balancing security, scalability, availability, performance, and cost.

A strong Enterprise VPC Architecture should be based on the actual requirements of the system. Additional services should not be introduced only to make the architecture appear more complex without providing clear value.

## Publication Information

- **Topic:** Upgrading Amazon VPC architecture for enterprise systems.
- **Published date:** July 29, 2026.
- **Platform:** AWS Study Groups.
- **Status:** Published.
- **Public link:** [Blog 4 on AWS Study Groups](https://www.facebook.com/groups/awsstudygroupfcj/permalink/2225997548165205/#)

