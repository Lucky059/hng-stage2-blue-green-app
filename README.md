Blue/Green Node.js Deployment with Nginx Overview:

This project demonstrates a Blue/Green deployment setup for Node.js services using Nginx as a reverse proxy and Docker Compose for orchestration. The goal is to achieve seamless traffic failover between two pre-built application containers — Blue (active) and Green (backup) — without rebuilding or modifying the app images.

Architecture Summary

Blue App (Primary) – Active by default, serves all requests in the normal state

Green App (Backup) – Standby instance, automatically takes over during Blue failure

Nginx Proxy – Handles routing, health-based failover, and request retries

Traffic Behavior

State Active Pool Request Handling Normal Operation Blue: All traffic goes to Blue Blue Failure Green Nginx retries requests to Green instantly ⚙️ Service Setup Service Port Description Nginx 8080 Public entrypoint Blue App 8081 Used by grader for chaos testing Green App 8082 Backup service (standby) Application Endpoints Endpoint Method Description /version GET Returns JSON + headers (X-App-Pool, X-Release-Id) /healthz GET Liveness probe /chaos/start POST Simulates downtime (500s or timeout) /chaos/stop POST Ends downtime simulation Environment Variables (.env)

All configuration is handled through environment variables for flexibility:

Variable Description BLUE_IMAGE Docker image for Blue service GREEN_IMAGE Docker image for Green service ACTIVE_POOL blue or green (controls Nginx routing) RELEASE_ID_BLUE Release ID for Blue RELEASE_ID_GREEN Release ID for Green PORT (optional) Overrides default app port Failover Logic

Blue is configured as the primary upstream, Green as backup.

Nginx uses:

Low max_fails and short fail_timeout for quick detection

Retries on 5xx and timeouts

Preserves all headers (X-App-Pool, X-Release-Id)

When Blue becomes unresponsive, Nginx seamlessly switches to Green, ensuring all client requests still receive successful responses (200 OK).

Testing the Deployment

Start Services

docker compose up -d

Verify Blue is Active

curl -i http://localhost:8080/version

Expected headers:

X-App-Pool: blue

Trigger Blue Failure

curl -X POST http://localhost:8081/chaos/start?mode=error

Verify Failover to Green

curl -i http://localhost:8080/version

Expected headers:

X-App-Pool: green

Recover Blue

curl -X POST http://localhost:8081/chaos/stop

Tools & Technologies

Docker Compose – Service orchestration

Nginx – Load balancing & automatic failover

Node.js (Pre-built Images) – Application containers

Highlights

Zero-downtime Blue/Green switch

Automatic health-based failover

Header preservation for version tracking

Fully parameterized via .env

No code or image rebuild required

Project Flow Diagram (placeholder) ┌────────────┐ │ Client │ └─────┬──────┘ │ ┌─────▼──────┐ │ NGINX │ └─────┬──────┘ │ │ (Active)│ │(Backup) ┌──────▼──────┐ ┌──────▼──────┐ │ BLUE APP │ │ GREEN APP │ └─────────────┘ └─────────────┘

📄 License

This project is created for educational and demonstration purposes — showcasing Blue/Green deployment concepts with Nginx and Docker Compose.

About
No description, website, or topics provided.
Resources
 Readme
 Activity
Stars
 0 stars
Watchers
 0 watching
Forks
 0 forks
Releases
No releases published
Create a new release
Packages
No packages published
Publish your first package
Languages
Shell
100.0%
Footer
© 2025
# hng13-stage3-devops
