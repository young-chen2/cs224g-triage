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
| **2** | **Young** | - Created UI for account management (login, separate experience for admin and users, etc) along with UI for document upload, tracking cases, and showing the RAG results the LLM uses to make a triage <br> - Integrated LangChain LLM workflow into the user-facing side of the chat; embed medical guidelines and triage guidelines and store them in FAISS, use RAG to boost LangChain response. Multi-agent workflow where ChatGPT prompts for complete symptoms and patient info while LangChain retrieval agent performs RAG and does the triage <br> - Prompt engineering to find the best prompts for the medical triage usecase <br> - Refactored entire codebase to use Poetry for dependency management and migrated to Next.js for UI (from Node) based on Sprint 1 feedback <br>
| **2** | **Cesar** | - Evaluated multiple medical guideline sources for pipeline integration <br> - Identified access limitations: <br> &nbsp;&nbsp;&nbsp;&nbsp; - Only Penn Medicine remained consistently accessible <br> &nbsp;&nbsp;&nbsp;&nbsp; - Government healthcare portals removed or relocated several guidelines <br> &nbsp;&nbsp;&nbsp;&nbsp; - Professional medical societies required institutional logins <br> &nbsp;&nbsp;&nbsp;&nbsp; - Clinical databases implemented stricter access controls <br> - Refined methodology due to access and formatting issues: <br> &nbsp;&nbsp;&nbsp;&nbsp; 1. Focused on Penn Medicine as the primary source <br> &nbsp;&nbsp;&nbsp;&nbsp; 2. Developed an advanced web scraping approach with structured validation <br> &nbsp;&nbsp;&nbsp;&nbsp; 3. Prioritized quality over quantity in guideline collection |
| **3** | **Young** | - Create database schemas and set up Supabase to store account information and triage cases <br> - Added logic to push triage cases to the backend DB after the LLM has made a decision, and to display these cases in the portal of the healthcare provider it was triaged to <br> - UI improvements and fixes to integrate the frontend and backend
| **4** | **Young** | - Debugged bugs in LLM agent performance issues, including more conversation context + adding more data about medical conditions to the FAISS vector DB made it more intelligent! <br> - UI improvements and polishing for final demo; added support for patients to create their own accounts <br> - A/B testing with different prompts and rephrasing: the LLM needs to be told very explicitly what to do in all caps! <br> - Wrote up technical portions of final presentation poster and made presentation/filmed demo <br>


# Getting Started with Triage 🏁

## TODOs ✔️

Our project uses the OpenAI ChatGPT API; we are using our own API key for development purposes. To run it locally, please create environmental variables as follows:
- From the project root, create `.env` and create the `OPENAI_API_KEY` variable and set it to your own OpenAI API key
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

1. Paste your own OpenAI API key into the `.env` file, along with our Supabase API keys and a flag called DEV_MODE:
```
SUPABASE_URL=https://glywofkvlxetpjaczarj.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdseXdvZmt2bHhldHBqYWN6YXJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA1MjMzODUsImV4cCI6MjA1NjA5OTM4NX0.-eddCtmxOD_QGAcMWdk7H92RgpVn7ioj3w8XdFHllrs
DEV_MODE=false
```

2. Start the FastAPI server from the root directory (`/cs224g-triage`) by running:
```bash
poetry run python run.py
```

The API will be available at http://localhost:8000. You can:
- View the API documentation at http://localhost:8000/docs
- Use curl to test: `curl http://localhost:8000/...`

Our project uses `Python 3.12.9`; activate a conda virtual environment to run Poetry if you aren't using it.
```
conda create -n myenv python=3.12
conda activate myenv
```

## Frontend Setup 🎨
Run the following from the `triage-next` directory.

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000).
