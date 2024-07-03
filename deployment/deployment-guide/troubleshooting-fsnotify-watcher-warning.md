---
description: >-
  Guide to fix "fsnotify watcher: too many open files" error while installing
  Helm.
---

# Troubleshooting: "fsnotify watcher" warning

This is not exactly and an error - you will be unable to see the full logs. To fix this&#x20;

* Login to K8Ss node
* create a file called `90-fs-inotify.conf` in `/etc/sysctl.d` folder&#x20;

```
fs.inotify.max_user_watches=2099999999
fs.inotify.max_user_instances=2099999999
fs.inotify.max_queued_events=2099999999
```

* Run `sysctl --system` as Root.
* Repeat the above for every K8s node in your cluster.
