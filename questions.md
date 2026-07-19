# RepoMind RAG Evaluation Questions

## EASY (15)

Q1
Difficulty: Easy
Category: Repository Overview
Question: What is the name of the FastAPI application instance defined in the backend, and in which file is it created?

Q2
Difficulty: Easy
Category: Configuration
Question: What port does the containerized application listen on, according to the Dockerfile?

Q3
Difficulty: Easy
Category: APIs
Question: Which HTTP method and path retrieves all stored transactions?

Q4
Difficulty: Easy
Category: APIs
Question: Which HTTP method and path is used to add a new transaction record?

Q5
Difficulty: Easy
Category: APIs
Question: Which HTTP method and path is used to request an expense prediction, and is the handler synchronous or asynchronous?

Q6
Difficulty: Easy
Category: Classes
Question: List all fields defined on the Transaction Pydantic model, along with their types.

Q7
Difficulty: Easy
Category: Classes
Question: What is the default value behavior of the Date field on the Transaction model if the client omits it?

Q8
Difficulty: Easy
Category: Dependencies
Question: Which Python web framework powers the backend API?

Q9
Difficulty: Easy
Category: Models
Question: Which machine learning model/library is used to forecast expenses?

Q10
Difficulty: Easy
Category: Configuration
Question: What base Docker image is used to build this application?

Q11
Difficulty: Easy
Category: Database
Question: Where is transaction data persisted, given the project has no traditional database?

Q12
Difficulty: Easy
Category: Folder Structure
Question: What is the name and title of the frontend HTML file, and what UI framework/library does it use?

Q13
Difficulty: Easy
Category: Security
Question: What CORS origins, methods, and headers does the backend allow?

Q14
Difficulty: Easy
Category: Utilities
Question: Which function in transaction.py is responsible for reading transactions from disk?

Q15
Difficulty: Easy
Category: Business Logic
Question: What multiplier is applied to the raw Prophet forecast value before it's returned by the /predict endpoint?

## MEDIUM (20)

Q16
Difficulty: Medium
Category: Data Flow / Multi-file reasoning
Question: Walk through exactly what happens, file by file, when a client sends POST /transactions.

Q17
Difficulty: Medium
Category: Models
Question: How does pred.py locate the model.pkl file at runtime? Explain the path construction.

Q18
Difficulty: Medium
Category: Database
Question: Why might new_transaction()'s persistence strategy be problematic if the API received concurrent requests?

Q19
Difficulty: Medium
Category: Business Logic
Question: Do student_expenses.csv and transactions.json use the same schema? Explain the difference.

Q20
Difficulty: Medium
Category: Error Handling
Question: What does load_transactions() return if the JSON file exists but is empty (0 bytes)?

Q21
Difficulty: Medium
Category: Error Handling
Question: What happens in load_transactions() if transactions.json does not exist at all?

Q22
Difficulty: Medium
Category: Models
Question: What preprocessing steps does training.py apply to the raw CSV before fitting the Prophet model?

Q23
Difficulty: Medium
Category: Models
Question: What interval_width is configured on the Prophet model during training?

Q24
Difficulty: Medium
Category: End-to-end workflow
Question: Trace a prediction request starting from the frontend's "Run Prediction" button all the way to the number displayed to the user.

Q25
Difficulty: Medium
Category: Data Flow
Question: What key-naming inconsistency exists in transactions.json regarding the date field?

Q26
Difficulty: Medium
Category: Multi-file reasoning
Question: How does the frontend's transaction rendering code defensively handle the "Date"/"date" key inconsistency found in transactions.json?

Q27
Difficulty: Medium
Category: Utilities
Question: What does the inline comment on get_all_transactions() say about its purpose, and is the implementation consistent with that comment?

Q28
Difficulty: Medium
Category: Functions
Question: In add_transaction(), why is data_dict['Date'] = str(data_dict['Date']) necessary?

Q29
Difficulty: Medium
Category: Dependencies
Question: requirements.txt lists orjson for "Faster JSON (optional)." Is orjson actually imported or used anywhere in the codebase?

Q30
Difficulty: Medium
Category: Models
Question: What columns does pred() construct in its input DataFrame before calling model.predict(), and why those specific names?

Q31
Difficulty: Medium
Category: Functions
Question: Does pred() actually use the yhat_lower value it computes and clips?

Q32
Difficulty: Medium
Category: Dependencies
Question: Which dependencies in requirements.txt are explicitly marked as conditional or optional via inline comments, and what are those comments?

Q33
Difficulty: Medium
Category: Architecture
Question: How does the Dockerfile's CMD instruction relate to the physical location of main.py, in terms of Python module resolution?

Q34
Difficulty: Medium
Category: Architecture
Question: Does marking predict_expanse() as async def provide any real concurrency benefit given how pred() is implemented?

Q35
Difficulty: Medium
Category: Security
Question: Does the Transaction Pydantic model enforce any constraint preventing a negative amount?

## HARD (15)

Q36
Difficulty: Hard
Category: Models / Error Handling
Question: Identify the discrepancy in training.py between the file-existence check and the file-save path, and explain why it could cause repeated retraining or a failed save.

Q37
Difficulty: Hard
Category: Data Flow / Multi-file reasoning
Question: Trace the exact sequence of type/value transformations a raw (Date, amount) pair undergoes between the /predict endpoint and the final returned number, citing every file involved.

Q38
Difficulty: Hard
Category: Security
Question: What specific security risk arises from combining allow_origins=["*"] with allow_methods=["*"] and allow_headers=["*"] on this particular application, given it has no authentication?

Q39
Difficulty: Hard
Category: Business Logic / Data Flow
Question: Given that transactions.json contains older records using a lowercase "date" key, would such a record pass validation if it were re-submitted as-is to POST /transactions?

Q40
Difficulty: Hard
Category: Architecture / Business Logic
Question: What is architecturally unusual about reusing the same Transaction model for both logging a real transaction (POST /transactions) and requesting a forecast (POST /predict), and which fields become semantically meaningless in the prediction context?

Q41
Difficulty: Hard
Category: Models
Question: Given that pred() places transaction.amount into the 'y' column of the DataFrame passed to model.predict(), does this amount actually influence the Prophet model's forecast?

Q42
Difficulty: Hard
Category: Utilities
Question: Is the abstraction provided by get_all_transactions() justified in this codebase, based on its actual implementation and the author's own comment?

Q43
Difficulty: Hard
Category: Database / APIs
Question: Does any transaction record in transactions.json carry a unique identifier (e.g., an id field)? What functionality does main.py lack as a consequence?

Q44
Difficulty: Hard
Category: Business Logic / Multi-file reasoning
Question: The CSV's Type column ("Fixed"/"Variable") and the JSON's type field ("income"/"expense") share a name but represent different concepts. Explain the distinction and how each is used (or discarded) in the codebase.

Q45
Difficulty: Hard
Category: Data Flow / Multi-file reasoning
Question: Is the Prophet model (model.pkl) trained on the live transaction data that users add through the /transactions endpoint?

Q46
Difficulty: Hard
Category: Architecture / End-to-end workflow
Question: Given there is no scheduled job or API endpoint that triggers training.py, how would model.pkl ever be refreshed after new transactions accumulate?

Q47
Difficulty: Hard
Category: Error Handling
Question: If load_transactions() raises a FileNotFoundError (because transactions.json is missing), what does the client calling GET /transactions/view receive, given the routes in main.py have no explicit exception handling?

Q48
Difficulty: Hard
Category: Architecture / Folder Structure
Question: Explain the relationship between the Dockerfile's WORKDIR changes and how Python resolves the from src.services.transaction import ... absolute import in main.py.

Q49
Difficulty: Hard
Category: Multi-file reasoning / Error Handling
Question: If backend/src/model/model.pkl were deleted, what would be the very first point of failure when the application starts, and why does it happen before the server accepts any requests?

Q50
Difficulty: Hard
Category: Data Flow / Multi-file reasoning
Question: Across the entire /predict request lifecycle, where does a numeric value get silently converted to a string, and what downstream effect (if any) does this have?
