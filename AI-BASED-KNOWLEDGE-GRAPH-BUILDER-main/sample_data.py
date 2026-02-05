eval_data = [

    # -------- General Dataset Questions --------
    {
        "question": "What types of data sources are used in this project?",
        "ground_truth": "The project uses multiple data sources including PDFs, emails, spreadsheets, and a database."
    },
    {
        "question": "What kind of data is handled by the system?",
        "ground_truth": "The system handles both structured data like spreadsheets and unstructured data such as PDFs and emails."
    },

    # -------- Spreadsheet / CSV Related --------
    {
        "question": "What information is stored in the spreadsheets?",
        "ground_truth": "The spreadsheets store product details such as product ID, name, price, brand, category, and customer review information."
    },
    {
        "question": "What review-related fields are present in the spreadsheet data?",
        "ground_truth": "The review data includes reviewer ID, review text, ratings, summary, and helpfulness scores."
    },
    {
        "question": "Which spreadsheet fields are useful for building recommendation systems?",
        "ground_truth": "Fields such as product ID, ratings, reviews, price, brand, and category are useful for recommendation systems."
    },

    # -------- PDF Related --------
    {
        "question": "What is discussed in the PDF documents?",
        "ground_truth": "The PDF documents describe the dataset, system architecture, data collection process, and recommendation system methodology."
    },
    {
        "question": "What steps of the system are explained in the PDF files?",
        "ground_truth": "The PDF files explain steps such as data collection, data wrangling, feature extraction, and system evaluation."
    },

    # -------- Email Related --------
    {
        "question": "What type of information is available in the email data?",
        "ground_truth": "The email data contains communication-related information, metadata such as sender, receiver, subject, and message content."
    },
    {
        "question": "How does email data differ from spreadsheet data?",
        "ground_truth": "Email data is unstructured text-based communication, while spreadsheet data is structured and organized in tabular form."
    },

    # -------- Knowledge Graph / Entity --------
    {
        "question": "What types of entities are extracted from the data?",
        "ground_truth": "Entities such as products, brands, users, reviewers, and organizations are extracted from the data."
    },
    {
        "question": "What relationships can be inferred between products and reviews?",
        "ground_truth": "Products are linked to reviews through ratings, review text, and reviewer information."
    },

    # -------- RAG / System Understanding --------
    {
        "question": "How does the chatbot retrieve relevant information?",
        "ground_truth": "The chatbot uses vector embeddings and FAISS similarity search to retrieve the most relevant document chunks."
    },
    {
        "question": "How does the system avoid answering outside the dataset?",
        "ground_truth": "The system retrieves answers only from the ingested documents stored in the vector database."
    },

    # -------- Demo / Viva Strong Questions --------
    {
        "question": "What makes this system different from keyword-based search?",
        "ground_truth": "The system uses semantic embeddings, allowing it to retrieve relevant information even if exact keywords are not present."
    },
    {
        "question": "How does the system trace answers back to source documents?",
        "ground_truth": "The system stores metadata with each text chunk, allowing answers to be linked back to their original source documents."
    }

]