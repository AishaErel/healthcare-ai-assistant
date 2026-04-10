# Careflow AI -- Healthcare AI Assistant

## What This Is:
AI-powered healthcare assistant built with IBM watsonx and IBM Cloudant database, designed to support doctors by providing efficient access to patient records, enabling the creation of new records, and converting consultation notes into structured medical documentation for an IBM Skills Build AI Experimental Lab Spring 2026 Project

## The Goal:
Create an AI system that reduces the administrative workload for medical professionals. We specifically aim to reduce the workload involved in retrieving and reviewing medical history as well as the process of formalizing the notes taken during the appointment. Reducing the administrative workload will enable the medical professional to focus more on patient care and their own well-being.


## Interface plan (tentative):
### Intro Page:
Purpose:
- Redirect to summarization agent
- Redirect to documentation agent


### Summarization agent:
Description: takes patient first and last name + DOB to query database for patient info/history + summary. May be supplied Reason for Visit which is the context
Tools:
- Ensure All Needed Information is present
- Get Patient Summary without Context
- Get Patient Summary with Context

### Documentation agent:
Description: takes doctor notes and tries to generate formal SOAP note documentation. Uploads this to the database when approved
Tools:
- Obtain Context
- Generate soap note
- Upload soap note to patient file in database

## What Has Been Implemented:
### (Week 6):
A chatbot interface has been implemented for the Summarization Agent. The Agent requests first and last name, as well as date of birth. The summarization agent is also capable of summarizing a patient's medical history, though this wasn't linked to the chatbot. The documentation agent could take doctor notes about the patient appointment and generate a SOAP note from them.

### (Week 7):
The Summarization Agent Chatbot interface now has tools linked, so it can take user input about patient information, fetch from the database, and provide a summary of the medical records retrieved. The Documentation Agent now has the capability to fetch medical history for a patient so that it has added context for the SOAP note generation.

## What Is Left:
- U/I improvements--Implement front page
- Prompt Fine Tuning -- Both the summarization agent and the documentation agent have some issues with inconsistent output, though this is more egregious with the summarization agent. We will try further fine tuning and switching from zero-shot to one-shot or few-shot prompting in the coming week to resolve this.
- Database write implementation -- The Documentation agent needs to be able to add new patient visit records after human approval. It will also need to create a patient file if the patient file does not yet exist
