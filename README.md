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
| **1** | **Young** | - Complete first prototype (React + JS) of the Triage Chat Interface <br> - Linked interface to the OpenAI and LangChain API <br> - System design and research on how to structure data/backend of Triage and how to integrate LangChain
| **1** | **Cesar** | - Research databases for diagnostic methodologies for primary care <br> - Adapt methodologies to established systems used in healthcare triage settings <br> - Communicate with potential stakeholders about the usefulness of applications <br> - Explore the potential to use Adobe UX for app interface <br> - Create json docs for triage and guidelines based on research <br>|


# Getting Started with Triage 🏁

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## TODOs ✔️

Our project uses the OpenAI ChatGPT API; we are using our own API key for development purposes. To run it locally, please replace the `REACT_APP_OPENAI_API_KEY` in the `.env` file with your own key (to avoid spending our API credits).

## Backend Setup 🔧

The backend uses FastAPI and LangChain for the API layer. Follow these steps to set up:

1. Navigate to the API directory:
```bash
cd src/api
```

2. Create a Python virtual environment (recommended):
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Paste your OpenAI API key into lang.py:

5. Start the FastAPI server:
```bash
uvicorn lang:app --reload
```
or if you're in root:
```bash
uvicorn src.api.lang:app --reload
```

The API will be available at http://localhost:8000. You can:
- View the API documentation at http://localhost:8000/docs
- Test the API (with a provided test case) at http://localhost:8000/test
- Use curl to test: `curl http://localhost:8000/test`

## Frontend Setup 🎨

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.
