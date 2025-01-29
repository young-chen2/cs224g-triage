# CS 224G: Triage

Team Members: Young Chen, César C. D. Baëta

![Triage_Logo_DallE](https://github.com/user-attachments/assets/dbbe05d2-3139-4889-b2b3-37b2d4e8ffd5)

# What we're doing 👨🏻‍⚕️
Triage aims to develop a chatbot to streamline patient triage in healthcare by leveraging generative AI and a database of evidence-based medical guidelines. The chatbot will interpret patient-reported symptoms, predict potential conditions, and recommend the appropriate care level—whether a physician, nurse practitioner, or physician assistant. This system is designed to alleviate physician workload, optimize resource allocation, and improve patient access to care. With the average wait time to see a physician increasing to 20 days in some cases, the administrative burden of managing care exacerbates this issue.  We expect to use RAG (retrieval-augmented generation) and agentic AI workflows (such as LangChain) to ensure a reliable and accurate triage.

Feel free to read our [project proposal](https://docs.google.com/document/d/1e8rt0J3iPCRJJVk_Oy_Pvra7Q6esKACeQp7xBpgs9GE/edit?usp=sharing) for more info.

# Sprint Progress 🏆

This table tracks contributions for each sprint by our team members.


| Sprint  | Team Member | Contribution |
|---------|--------------|---------------|
| **1** | **Young** | - Complete first prototype (React + JS) of the Triage Chat Interface <br> - Linked interface to the OpenAI and LangChain API <br> - ...
| **1** | **Cesar** | - [Contribution 1] <br> - [Contribution 2] <br> - [Contribution 3] |


# Getting Started with Triage 🏁

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## TODOs ✔️

Our project uses the OpenAI ChatGPT API; we are using our own API key for development purposes. To run it locally, please replace the `REACT_APP_OPENAI_API_KEY` in the `.env` file with your own key (to avoid spending our API credits).

## Available Scripts

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
