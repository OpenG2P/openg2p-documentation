# Superset

### Helm install

`helm --kubeconfig ~/.kubectl/dev.yaml -n superset install --set extraSecretEnv.SUPERSET_SECRET_KEY=YU87e superset superset/superset`

A secret needs to be set otherwise the install fails

Port forward to access from your machine:

`kubectl --kubeconfig ~/.kubectl/dev.yaml -n superset port-forward service/superset 8088:8088 --namespace superset`

### Superset DB

Superset has its own Postgres installed as part of the above helm chart. To access Postgres from your desktop, port forward as&#x20;

`kubectl --kubeconfig ~/.kubectl/dev.yaml -n superset port-forward service/superset-postgresql 5432:5432`&#x20;

To access the DB

`psql --host=localhost -p 5432 -d superset -U superset`

Password: `superset`
