# Grievance Redress Mechanism

## Introduction

The module is a comprehensive support ticketing system designed for the OpenG2P platform. It enables organizations to efficiently manage support requests from beneficiaries, track issue resolution, and ensure accountability within support teams.  The module is designed to be independent and does not rely on other modules. However, it can be extended or integrated with other applications such as program management, beneficiary registries, or portals.

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

**Ticket Lifecycle**

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

* Chatter: All ticket-related communication and activity is logged for transparency
* External References: Fields for program IDs, application IDs, or ERNs allow linking with other systems.
* Extensibility: Can be easily extended to integrate with portals, program management, or registries.

## Security

Access rights are defined for different user roles (agents, leaders, admins).

Only authorized users can view or modify tickets as per their role.

## Technical Details

The Support Desk module is built on top of Odoo’s ORM and Messaging framework, ensuring full integration with activities, chatter, and notifications.

#### Data Models

1. **Support Category (`support.category`)**
   * Hierarchical structure (self-referencing parent/child).
   * Used to organize tickets.
   * Tracks related tickets via `ticket_ids` and computed `ticket_count`.
2. **Support Stage (`support.stage`)**
   * Defines ticket workflow stages (e.g., New, In Progress, Done).
   * Supports team-specific stages.
   * Allows auto-email on stage change via linked `mail.template`.
3. **Support Tag (`support.tag`)**
   * Simple tagging system with colors.
   * Used to classify and search tickets.
4. **Support Team (`support.team`)**
   * Represents helpdesk teams.
   * Tracks team leader and members.
   * Computes ticket counts for workload monitoring.
5. **Support Ticket (`support.ticket`)**
   * Core ticket model.
   * Fields:
     * Metadata: `number`, `name`, `priority`, `stage_id`.
     * Assignment: `team_id`, `user_id`.
     * Creator details: `creator_name`, `creator_email`, `creator_phone`, `creator_address`.
     * Resolution info: `resolution_message`, `resolution_time`, `closed_date`.
   * Features:
     * Auto ticket numbering via `ir.sequence`.
     * “Assign to Me” action (`action_assign_to_me`).
     * Full chatter and activities support.

### Conclusion

The  module provides a robust, integrated solution for managing support operations within the OpenG2P ecosystem. Its flexible design, strong integration points, and user-friendly interface make it a valuable tool for organizations aiming to deliver high-quality support to beneficiaries.
