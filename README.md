# Sentry OSS Engineer Screening Exercise

This is a simple Flask app that uses [CouchDB](https://couchdb.apache.org/)/[Cloudant](https://www.ibm.com/cloud/cloudant) as its data store.

## Tasks

You have the following tasks:

1. The Dockerfile included is incomplete and does not work. Make the app work in a Docker container
2. Set the application up using [Docker Compose](https://docs.docker.com/compose/) so it is testable
3. Write a smoke test to ensure the application is up and accepting requests successfully
4. Wire up building the Docker image and the smoke test in CI so it runs on each commit/push/PR. Your options are GitHub Actions, Google Cloud Build, and Travis CI, in that preference order.

## Resources

You may find the following resources helpful:

- [https://hub.docker.com/_/couchdb?tab=description](https://hub.docker.com/_/couchdb?tab=description)
- [https://docs.docker.com/compose/compose-file/](https://docs.docker.com/compose/compose-file/)
- [https://docs.docker.com/compose/compose-file/#restart](https://docs.docker.com/compose/compose-file/#restart)
- [https://github.com/getsentry/snuba/blob/master/docker-compose.yml](https://github.com/getsentry/snuba/blob/master/docker-compose.yml)

## Disclaimer

This repo is adapted from https://github.com/IBM-Cloud/get-started-python/
