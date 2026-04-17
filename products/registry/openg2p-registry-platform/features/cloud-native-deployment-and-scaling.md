# Cloud-Native deployment and scaling

The Base Registry is implemented as a set of microservices, with clear separation between registry APIs, ingestion pipeline workers, and metadata management. All components can be scaled horizontally based on workload, allowing the registry to handle high-volume ingestion of events or bursty change approval processes. The platform is compatible with container orchestration environments such as Kubernetes and supports centralized logging, metrics, and distributed tracing for operational visibility.
