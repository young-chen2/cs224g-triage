# CS 224G: Triage

Team Members: Young Chen, César C. D. Baëta

![Triage_Logo_DallE](https://github.com/user-attachments/assets/dbbe05d2-3139-4889-b2b3-37b2d4e8ffd5)

# Goals 👨🏻‍⚕️
Our goal is to develop a chatbot that streamlines patient triage in healthcare by leveraging generative AI and a database of evidence-based medical guidelines. This tool addresses the growing need for physicians to work at the top of their licenses while maximizing hospital resources. It also improves patient access to appropriate care, reducing the stress and anxiety that come with delayed treatment.

Beyond enhancing efficiency, our chatbot aligns with value-based care metrics—an increasingly important measure in the healthcare system. It interprets patient-reported symptoms, predicts potential conditions, and recommends the appropriate level of care, whether that be a physician, nurse practitioner, or physician assistant. This ensures that healthcare professionals remain involved in decision-making while optimizing workflows.

With physician wait times averaging up to 20 days in some cases, the administrative burden of managing care only exacerbates the issue. Our system is designed to alleviate physician workload, optimize resource allocation, and improve patient access to timely care. We plan to achieve this by integrating RAG (retrieval-augmented generation) and agentic AI workflows (such as LangChain) to ensure a reliable, accurate, and scalable triage solution.

Feel free to read our [project proposal](https://docs.google.com/document/d/1e8rt0J3iPCRJJVk_Oy_Pvra7Q6esKACeQp7xBpgs9GE/edit?usp=sharing) for more info.

# Sprint Progress 🏆

This table tracks contributions for each sprint by our team members.
- Young (Technical/Engineering/AI): Computer science, concentrating in AI and Systems
- Cesar (PM/Research): Epidemiology clinical research and healthcare background with knowledge about patient-centered value-based care 

| Sprint  | Team Member | Contribution |
|---------|--------------|---------------|
| **1** | **Young** | - Complete first prototype (React + JS) of the Triage Chat Interface <br> - Linked interface to the OpenAI and LangChain API: interface allows conversation with gpt-4o-mini, and launching the API layer at localhost:8000 allows you to test the LangChain workflow at route `/test` <br> - System design and research on how to structure data/backend of Triage and how to integrate LangChain
| **1** | **Cesar** | - Research databases for diagnostic methodologies for primary care <br> - Adapt methodologies to established systems used in healthcare triage settings <br> - Communicate with potential stakeholders about the usefulness of applications <br> - Explore the potential to use Adobe UX for app interface <br> - Create json docs for triage and guidelines based on research <br>|


# Getting Started with Triage 🏁

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## TODOs ✔️

Our project uses the OpenAI ChatGPT API; we are using our own API key for development purposes. To run it locally, please create environmental variables as follows:
- In `.env`, set `OPENAI_API_KEY` to your own OpenAI API key
- In `.env.local`, set `NEXT_PUBLIC_OPENAI_API_KEY` to your own OpenAI API key

## Development Setup with Poetry 👩🏻‍💼

This project uses Poetry for Python dependency management. Here's how to get started:

1. Install Poetry (if you haven't already):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   --OR--
   brew install poetry
   ```

2. Clone this repository and navigate to the project directory (root)

3. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
   If this doesn't work, try using a Python VENV:
      ```bash
   conda create -n api-env python=3.11
   conda activate api-env
   poetry install
   ```

5. Run the FastAPI server/React App:
   ```bash
   poetry run uvicorn src.api.lang:app --reload
   poetry run npm start
   ```

### Common Poetry Commands

- Add a new dependency:
  ```bash
  poetry add package-name
  ```
- Remove a dependency:
  ```bash
  poetry remove package-name
  ```
- Update dependencies:
  ```bash
  poetry update
  ```
- Activate the virtual environment:
  ```bash
  poetry shell
  ```

## Backend Setup 🔧

Triage's backend uses FastAPI and LangChain for the API layer. Follow these steps to set up:

1. Paste your own OpenAI API key into our `.env` files and navigate to the backend API directory `src/api`:

2. Start the FastAPI server:
```bash
poetry run uvicorn lang:app --reload
```
or if you're in root:
```bash
poetry run uvicorn src.api.lang:app --reload
```

The API will be available at http://localhost:8000. You can:
- View the API documentation at http://localhost:8000/docs
- Test the API (with a provided test case) at http://localhost:8000/test
- Use curl to test: `curl http://localhost:8000/test`

## Frontend Setup 🎨

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000).
