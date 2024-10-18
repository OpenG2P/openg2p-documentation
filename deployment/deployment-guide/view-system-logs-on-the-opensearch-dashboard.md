# View System Logs on the OpenSearch Dashboard

This guide will walk you through how to access, filter, and interpret system logs on the OpenSearch dashboard. Our setup leverages a reporting framework that collects logs from Docker containers and indexes them in OpenSearch for easy access and filtering.

### Viewing system logs on opensearch dashboard

1. **Access the OpenSearch Dashboard**\
   Open the OpenSearch Dashboard in your browser using the provided URL. Ensure you have the necessary credentials to log in.
2. **Navigate to the Logs Section**
   * Go to **Discover** from the left-hand menu.
   * Select the relevant **log index pattern** (e.g., `*.public.res_partner*`) to load logs.
3. **Filter Logs by Severity (INFO, ERROR, etc.)**
   * Use the search bar at the top to filter logs. For example
     * `level:INFO` to see informational logs.
     * `level:ERROR` to view error logs.
   * You can combine filters using logical operators, like
     * `level:ERROR AND service:postgres`
4. **Customize Time Range**
   * Use the time picker in the top right corner to filter logs for specific periods (e.g., Last 15 minutes, Today, or Custom Range).
5. **Save Searches and Views**
   * After setting up filters, click **Save** to store frequent searches for quick access.
   * Use **Add Filter** or **Edit Columns** to refine how log entries are displayed.
6. **Explore and Export Logs**
   * Click on individual log entries to view details.
   * Use the **Share** button to generate reports or export logs if needed.
   *   And you can see the image below for all the operations above.\


       <figure><img src="../../.gitbook/assets/image.png" alt=""><figcaption><p>Opensearch-dashboard.png</p></figcaption></figure>
   * This framework provides a streamlined way to monitor and analyze logs effectively. Use filters regularly to narrow down critical information like errors or warnings.
