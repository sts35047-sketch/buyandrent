# Buy or Wait Backend

AI-powered financial agent that decides on user affordability (affordable_now, affordable_with_plan, affordable_later, not_affordable).

## Running the application
1. Place the dataset in the `dataset/` directory.
2. Build and run with Docker Compose:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   export GEMINI_API_KEY="your-api-key"
   docker-compose up --build
   ```

## Running the CLI
```bash
python main.py --input dataset/requests.csv --output output.csv
```
