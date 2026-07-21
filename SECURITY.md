# Security policy

Report suspected vulnerabilities privately to the repository maintainers through GitHub's private vulnerability reporting feature. Do not include identity images, model artifacts, credentials, or customer data in a public issue.

The reference API is stateless and must not log uploaded image bytes. Operators may enable its optional `X-API-Key` check for scoring requests by providing the configured key file. TLS termination, key distribution, abuse controls, request accounting, retention policy, and deployment isolation remain operator responsibilities. The service score is not an authentication result and must not be represented as one.
