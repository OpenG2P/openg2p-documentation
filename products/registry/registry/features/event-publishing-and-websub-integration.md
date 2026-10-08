# Event Publishing and WebSub Integration

When an approved registry change should leave the registry, the outgestion
pipeline renders it with a Jinja template and publishes it through the shared
[WebSub](../../../../platform/platform-services/websub/README.md) hub.
Subscribers receive the rendered payload on the topic they joined. The same
change can be published in more than one external shape by using a separate
topic and template for each shape.

That path is for register-change events. It is specified in the
[Outgestion Pipeline](outgestion-pipeline.md).

Asynchronous partner search uses the same hub, but it publishes a search
result for one partner rather than a register change. That behaviour is
specified in [Partner Register Search](partner-register-search.md).

Topic registration, callback challenges, and delivery signatures belong to the
hub, not to either registry feature. See
[Subscription and delivery](../../../../platform/platform-services/websub/subscription.md).
