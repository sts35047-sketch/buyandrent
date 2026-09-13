# Buy or Wait Backend

AI-powered financial agent that decides on user affordability (affordable_now, affordable_with_plan, affordable_later, not_affordable).

## Approach Overview
Our solution tackles the affordability problem by analyzing a user's 90-day projected financial buffer. The core logic involves:
1. **Multimodal Extraction**: Using Gemini to extract missing transaction values from chat messages and receipt images.
2. **Expense Classification**: Identifying recurring vs. flexible expenses and extrapolating them over a 90-day rolling window to calculate the daily liquid cash minimum (`safe_amount`).
3. **Smart Decision Engine**: Recommending payment strategies (full_payment, installments, wait) by ranking options based on maximizing the user's safety buffer, fulfilling the request date, and minimizing total cost. We intelligently suggest reducing flexible expenses if it prevents an overdraft.

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
