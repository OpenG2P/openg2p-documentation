# Grievance Redress Mechanism

## Introduction

The module is a comprehensive support ticketing system designed for the OpenG2P platform. It enables organizations to efficiently manage support requests from beneficiaries, track issue resolution, and ensure accountability within support teams. The module is tightly integrated with other OpenG2P components, such as program management and beneficiary registry, to provide a seamless support experience.

## Features

* **Ticket management**: Create, assign, and track support tickets linked to beneficiaries, programs, cycles, and entitlements.
* **Team management**: Organize support staff into teams, assign tickets, and monitor workloads.
* **Stage & workflow management**: Define custom ticket stages (e.g., New, In Progress, Done) and visualize progress using Kanban boards.
* **SLA tracking**: Monitor response and resolution times to ensure service level agreements are met.
* **Knowledge base integration**: Link tickets to knowledge base articles for faster issue resolution.
* **Portal access**: Allow beneficiaries to submit and track tickets via a self-service portal.
* **Tagging & categorization**: Classify tickets by category and tags for better reporting and filtering.
* **Chatter integration**: Use Odoo’s chatter for internal communication, logging activities, and tracking ticket history.

### Functional Design

#### Ticket Lifecycle

* Creation: Tickets can be created by support staff or directly by beneficiaries (via portal).
* Assignment: Tickets are assigned to teams and/or individual users.
* Progression: Tickets move through defined stages (e.g., New → In Progress → Done).
* Closure: Tickets are closed when resolved, with resolution time tracked.

#### User Roles

* Support agents: Can view, create, and manage tickets assigned to them or their team.
* Team leaders: Oversee team tickets, reassign as needed, and monitor performance.
* Beneficiaries: Can submit and track their own tickets via the portal.
* Administrators: Configure stages, categories, teams, and access rights.

#### Integration Points

* Programs & beneficiaries: Tickets can be linked to specific programs, cycles, entitlements, and beneficiaries.
* Chatter: All ticket-related communication and activity is logged for transparency

## Security

Access rights are defined for different user roles (agents, leaders, admins).

Only authorized users can view or modify tickets as per their role.

### Conclusion

The  module provides a robust, integrated solution for managing support operations within the OpenG2P ecosystem. Its flexible design, strong integration points, and user-friendly interface make it a valuable tool for organizations aiming to deliver high-quality support to beneficiaries.
