---
title: "Event 1: FCAJ Community Day – June 2026"
date: 2024-01-01
weight: 1
chapter: false
pre: " <b> 4.1. </b> "
---

## Event Name

FCAJ Community Day – June 2026: Data Driven, AI Risen

This community event focused on AWS Cloud and AI. It included presentations related to Cloud careers, AI Agents, Voice AI, DevOps Automation, Amazon Q, and MCP connection security.

## Time

9:00 AM, Saturday, June 27, 2026.

## Location

Floors 26 and 36, Bitexco Financial Tower, 02 Hai Trieu Street, Ho Chi Minh City.

For this report, I attended the event online through the AWS Study Group livestream on Youtube.

## Role

Online participant.

I followed the presentations, recorded the main technical points, and analyzed how the introduced solutions could be applied to Cloud and AI projects.

## Main Content

The event covered several topics related to the adoption of AI and Cloud technologies in enterprise environments.

### Changes in Cloud Careers in the AI Era

The first presentation discussed the impact of AI on the work of Cloud Engineers and Solution Architects.

AI can assist with coding, log analysis, and the automation of operational tasks. However, these capabilities also require engineers to develop a deeper understanding of system architecture, security, costs, and incident response.

AI can improve productivity, but engineers remain responsible for validating the results and making appropriate technical decisions.

### Building Voice AI Agents for the Vietnamese Market

The speakers introduced the general Voice AI Agent workflow:

Speech-to-Text -> Large Language Model -> Text-to-Speech

Important challenges included:

- Reducing system latency.
- Accurately recognizing Vietnamese speech.
- Handling regional accents and pronunciation differences.
- Detecting when users interrupt the Agent.
- Maintaining conversational context.
- Controlling costs and maintaining system stability.

Voice AI Agents can also be connected to business tools to perform practical tasks instead of only answering questions.

### Automating Incident Response with AWS DevOps Agent

AWS DevOps Agent was introduced as a solution that can assist in collecting logs, analyzing alerts, identifying root causes, and recommending remediation steps.

This solution may reduce incident-resolution time compared with manually reviewing multiple data sources. However, engineers must still verify the identified cause and evaluate the safety of the proposed actions.

### Applying Amazon Q to Recruitment

One use case demonstrated how Amazon Q could read multiple CVs, compare candidate skills with job descriptions, and generate evaluation reports.

This solution could reduce the time required for initial CV screening. It also demonstrated that enterprise AI must be deployed in a controlled environment to protect personal and candidate data.

### Securing MCP Connections

The final presentation discussed the risks of exposing an MCP Server directly to the Internet. Potential risks include unauthorized access, denial-of-service attacks, and data theft during transmission.

The proposed solution was to place the MCP Server inside a private network by using a VPC, Private subnet, private endpoint, and internal DNS resolution.

This approach allows data exchanged between an AI Assistant and enterprise tools to remain outside the public Internet, thereby reducing the attack surface and improving access control.

## Participation Evidence

Personal participation evidence:

![Event 1 participation evidence](/images/3-Events/Evidence_Events%201.jpg)

## Lessons Learned

After the event, I recognized that AI creates meaningful value only when it is integrated with reliable data and business processes.

A conventional chatbot may answer questions, but an enterprise AI system must also be able to retrieve trusted data, use tools, enforce access control, and record its activities.

The Voice AI presentation helped me understand that combining STT, LLM, and TTS components can be relatively straightforward at the prototype level. However, production deployment requires teams to address latency, user interruption, regional accents, cost, and system stability.

The AWS DevOps Agent session demonstrated that AI can provide considerable support in log analysis and incident resolution. Nevertheless, engineers must understand the system architecture to validate the identified cause and the recommended remediation plan.

The most important lesson for me was that security must be considered from the design stage. When AI is connected to email, databases, project-management systems, or internal tools, a single configuration error may expose significant amounts of sensitive data.

Therefore, systems should apply the principle of least privilege, use private networking when appropriate, and maintain control over every action performed by an AI Agent.

## Personal Contribution

My personal contribution was to record and classify the event content into three main categories:

- AI and Agent applications.
- Cloud operations.
- System and connection security.

I also related these concepts to my internship project, particularly the use of AI for CV analysis, candidate-job matching, and the protection of personal data stored in the system.

Through this review, I identified several requirements that should be considered when developing AI features, including data-access permissions, activity tracking, user-confirmation mechanisms, and the protection of sensitive information.
