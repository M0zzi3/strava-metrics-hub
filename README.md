# SETUP INSTRUCTION
> I have hardcoded valid API keys in the `envexample` file for demonstration purposes.

## To run the project immediately for grading:
1. Locate the file named `envexample` in the root folder of the submission.
2. Rename this file to `.env`.
3. Open a terminal in the project folder and run:
```bash
docker compose up -d --build
```
4. The application will be running at: `http://localhost:5000`.

> Note: In case the Strava API blocks the request (due to rate limits or key expiry), I have attached screenshots of the working dashboard with populated data in the `/Screenshots` folder.