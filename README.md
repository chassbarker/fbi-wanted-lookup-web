# FBI Wanted Lookup

A Streamlit browser app by Chassidy Barker, adapted from an ITSE 1359 Python API project with ChatGPT assistance.

Search public FBI listings by field office, choose a page, and display titles, descriptions, and official links. No API key is configured. Identical requests are cached for five minutes to reduce traffic. Listings include missing persons and requests for information as well as wanted persons.

## Run on Windows

Keep this project in a separate folder from your class submission. Open its folder in VS Code, then run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the localhost address printed in your terminal. Keep the terminal running while using the local app. A localhost address is only for your computer, not a public sharing link.

## Share online free with Streamlit Community Cloud

1. Create a GitHub repository named `fbi-wanted-lookup-web` and upload `app.py` and `requirements.txt` (optionally this README).
2. Sign in at https://share.streamlit.io/ and connect your GitHub account.
3. Choose **Create app**, select the repository and branch, and set the main file path to `app.py`.
4. Deploy. Once deployment succeeds, send people the resulting `https://...streamlit.app` link or add it to your portfolio.

Community Cloud is a free hosting service. Account sign-in and an actual deployment are required before a shareable app URL exists. See https://docs.streamlit.io/deploy/streamlit-community-cloud for current terms and limits.

## Behavior and limits

- Blank office searches without an office filter; San Antonio becomes `sanantonio`.
- Displays only the chosen number of items on the chosen API page, not every matching record.
- Shows friendly messages for no results, timeouts, HTTP/network failures, and invalid JSON/schema.
- Requests happen on form submission, not on every keystroke.
- No photos or graphic case details are downloaded. Descriptions are plain text.
- This independent project is not affiliated with the FBI. Check official listings for current information. A listing does not establish guilt.

Source: https://www.fbi.gov/wanted/api
Endpoint: https://api.fbi.gov/wanted/v1/list
