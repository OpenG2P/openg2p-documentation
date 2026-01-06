# Implement backup with Barman

### Why [Barman](https://www.pgbarman.org/) ? <a href="#a540" id="a540"></a>

PostgreSQL, implements PITR thanks to use of WAL files and provides way to archive those. We could technically use plain rsync to backup our WAL files and other commands provided by PostgreSQL but Barman is more convenient. It helps manage the backups and makes the whole process much easier. You could, however, technically do it without. To understand all the concepts behind this backup solution I suggest you read the links mentioned in [http://docs.pgbarman.org/release/2.4/#before-you-start](http://docs.pgbarman.org/release/2.4/#before-you-start) which describes in more details some of the concepts we already talked about.\
<br>
