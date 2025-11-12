---
description: >-
  This guide explains how to deploy Strapi in any environment to enable
  integration, testing, and production readiness.
---

# Deployment of Strapi

## **Installation of Strapi CMS**

We are implementing **Strapi** as the **CMS for the Beneficiary portal UI** to manage and display dynamic content such as text, news, and announcements.

This guide explains how to deploy Strapi in any environment to enable integration, testing, and production readiness.

***

## **1. Prerequisites**

Before deploying, ensure you have:

* Access to the Kubernetes **cluster** where Strapi will be deployed
* Correct **namespace permissions**
* A **PostgreSQL** instance available
* Docker image of Strapi built and pushed to the container registry

***

## **2. Clone the deployment repository**

All Kubernetes manifests are available in the following GitHub repository:

👉 [https://github.com/shaketshubham/strapideploy](https://github.com/shaketshubham/strapideploy)

***

## **3. Deployment files**

The repository contains the following manifests:

1. `postgres-pvc.yaml` — Persistent Volume Claim for PostgreSQL
2. `postgres-service.yaml` — PostgreSQL service definition
3. `postgres-deployment.yaml` — PostgreSQL deployment configuration
4. `pvc.yaml` — Persistent Volume Claim for Strapi uploads
5. `deployment.yaml` — Strapi deployment manifest
6. `service.yaml` — Strapi service configuration
7. `virtualservice.yaml` — Istio VirtualService for external access

***

## **4. Deployment steps**

Run the following commands to deploy Strapi.

#### **Step 1: Set namespace context**

```bash
kubectl config use-context <cluster-name>
kubectl config set-context --current --namespace=<namespace>
```

#### **Step 2: Deploy PostgreSQL**

```bash
kubectl apply -f postgres-pvc.yaml -n <namespace>
kubectl apply -f postgres-service.yaml -n <namespace>
kubectl apply -f postgres-deployment.yaml -n <namespace>
```

#### **Step 3: Deploy Strapi PVC**

```bash
kubectl apply -f pvc.yaml -n <namespace>
```

#### **Step 4: Deploy Strapi application**

```bash
kubectl apply -f deployment.yaml -n <namespace>
kubectl apply -f service.yaml -n <namespace>
```

#### **Step 5:  Configure external access**

```bash
kubectl apply -f virtualservice.yaml -n <namespace>
```

***

## **5. Verify the deployment**

1. Check if all pods are running:

```bash
kubectl get pods -n <namespace>
```

2. Check services:

```bash
kubectl get svc -n <namespace>
```

3. Once running, open the Strapi Admin Panel using the configured service or ingress URL.

***

## **6. Environment configuration**

In the **deployment.yaml**, ensure these environment variables are set:

| Variable            | Description                                      |
| ------------------- | ------------------------------------------------ |
| `DATABASE_HOST`     | PostgreSQL service name                          |
| `DATABASE_PORT`     | Database port (default: 5432)                    |
| `DATABASE_NAME`     | Strapi database name                             |
| `DATABASE_USERNAME` | PostgreSQL username                              |
| `DATABASE_PASSWORD` | PostgreSQL password                              |
| `APP_KEYS`          | Application keys (comma-separated)               |
| `JWT_SECRET`        | Secret key for authentication                    |
| `NODE_ENV`          | Set to `production` or `development` as required |

> 💡 Configure these values either via **Kubernetes Secrets** or **Rancher environment variables**.

***

## **7. CORS and API access**

Update the `config/middlewares.js` file or use environment variables to allow frontend domains.

Example:

```js
module.exports = [
  'strapi::logger',
  'strapi::errors',
  {
    name: 'strapi::security',
    config: {
      contentSecurityPolicy: {
        useDefaults: true,
        directives: {
          'connect-src': ["'self'", 'https:', 'http:', 'https://portal.openg2p.org'],
        },
      },
    },
  },
  'strapi::cors',
];
```

***

## **8. Testing API connection**

Once deployed, you can test API connectivity using curl or a browser:

```bash
curl https://<your-strapi-domain>/api/news
```

If you receive a JSON response, Strapi is successfully serving data.

***

## **9. Repository reference**

All manifests are available in the GitHub repository:\
👉 [https://github.com/shaketshubham/strapideploy](https://github.com/shaketshubham/strapideploy)

***

