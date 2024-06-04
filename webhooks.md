# Webhooks, Asynchronous Integration Pattern for WSO2 (REST)

In certain integrations, synchronous communication can fail due to high payloads or timeout limits, and KAFKA is not always a viable option. To address this, we support Webhooks an asynchronous integration pattern using WSO2 (REST). This solution is compatible with OAS hosted both on-premises and in AWS.

## Table of Contents
1. [Overview](#overview)
2. [REST Call Triggering Asynchronous Invocation](#rest-call-triggering-asynchronous-invocation)
3. [Asynchronous Service Result Handling](#asynchronous-service-result-handling)
4. [Error Handling and Retry Mechanism](#error-handling-and-retry-mechanism)
5. [Configuration](#configuration)

## Overview
Webhooks,the asynchronous integration pattern, allows for efficient job processing and result handling through REST API calls, ensuring robustness and reliability in various hosting environments. This documentation outlines the key components and functionalities provided.

## REST Call Triggering Asynchronous Invocation
### Objective
Enable asynchronous job processing, through REST API calls with specific header requirements.

### Details
- **Endpoint Trigger:** When a REST call hits an OAS WSO2 API endpoint with a header named `callback-url`, it initiates an asynchronous job.
- **Immediate Response:** The API responds immediately, confirming whether the job was successfully invoked.
- **Header Propagation:** Essential headers, such as `callback-url` and `x-correlation-id`, are forwarded to all invoked services.

### Implementation Steps
1. **Receive REST Call:**
   - API endpoint receives a REST call with `callback-url` in the header.
2. **Initiate Asynchronous Job:**
   - Asynchronous job is initiated based on the REST call.
3. **Immediate API Response:**
   - Send an immediate response confirming job invocation status.
4. **Propagate Headers:**
   - Forward `callback-url` and `x-correlation-id` to all relevant services.

## Asynchronous Service Result Handling
### Objective
Manage and communicate the results of asynchronous services efficiently and securely.

### Details
- **Result Communication:** Upon completion, each service uses REST POST to send results to the `callback-url` webhook.
- **Error Reporting:** Any errors are similarly communicated to the webhook.
- **Service User Switch:** Services switch to a service-user account for webhook authentication.
- **S3 Offloading:** For results exceeding a predefined size, compressing and offloading to S3 occurs, and a pre-signed download URL is generated.
- **Indirect Result Messaging:** In S3 offloading cases, an indirect result message is sent to the webhook, detailing download information as a pre-signed URL or the used pre-signed upload URL.

### Implementation Steps
1. **Result Communication:**
   - Service completes job and sends result to `callback-url` via REST POST.
2. **Error Reporting:**
   - Send error details to `callback-url` if job fails.
3. **Service User Authentication:**
   - Switch to service-user account for webhook authentication.
4. **S3 Offloading:**
   - Compress and offload large results to S3, generating a pre-signed download URL.
5. **Indirect Result Messaging:**
   - Send indirect result message with pre-signed URL details to `callback-url`.

## Error Handling and Retry Mechanism
### Objective
A robust error handling and retry mechanism for failed webhook communications.

### Details
- **Retry Triggers:** Non-responsiveness or specific errors (408, 502, 503, 504) from the webhook initiate a retry sequence.
- **Result Preservation:** The result is uploaded to an S3 bucket (if not already done) and the service information, along with the S3 location, is logged in an `OasWebhookRetry` database object.
- **Retry Process:** A scheduled task periodically scans the error database objects and attempts to resend results, packaged in an indirect result message.
- **Backoff Strategy:** The retry backoff mechanism gradually increases the wait time between retries when a webhook communication fails. It starts with a base delay of 1 second and doubles this delay with each subsequent retry attempt, up to a maximum of 1 hour. If the total retry duration exceeds 12 hours, the system stops attempting retries and marks the task as failed. This approach ensures that retries are spaced out more over time, reducing the risk of overwhelming the server. The retry count and the next attempt time are updated after each retry attempt.

### Implementation Steps
1. **Identify Retry Triggers:**
   - Detect non-responsiveness or specific errors from the webhook.
2. **Preserve Result:**
   - Upload result to S3 and log service information in `OasWebhookRetry` database.
3. **Scheduled Retry Task:**
   - Periodically scan the error database and attempt to resend results.
4. **Apply Backoff Strategy:**
   - Implement extended back-off periods for consecutive failures, ceasing after 24 hours.

## Configuration
*(This section will be populated with configuration details.)*

---
