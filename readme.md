# AI Car Recommendation

This project provides an AI car research assitant UI powered by a Python-based CrewAI agent. It enables users to conduct AI-assisted car research, receive recommendations, and explore detailed reviews for selected items.

**(Optional: Add a link to your live demo if you have one)**
**(Optional: Add a link to your tutorial video if you create one)**
---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
  - [1. Clone Repository](#1-clone-repository)
  - [2. Backend Agent (Python/CrewAI)](#2-backend-agent-pythoncrewai)
  - [3. Frontend UI (Next.js)](#3-frontend-ui-nextjs)
- [API Keys Required](#api-keys-required)
- [Running the Application](#running-the-application)
  - [1. Start the Backend Agent](#1-start-the-backend-agent)
  - [2. Start the Frontend UI](#2-start-the-frontend-ui)
  - [3. Access the Application](#3-access-the-application)
- [Troubleshooting](#troubleshooting)
- [(Alternative) JS Agent Setup Notes](#alternative-js-agent-setup-notes)

---

## Overview

This application offers an intelligent interface for AI-driven car research. Users can define research questions, and the CrewAI agent backend utilizes tools like web search (via Tavily) and advanced language models (via OpenRouter or OpenAI directly) to gather information, generate tailored recommendations, and provide in-depth reviews upon request. The frontend is built with Next.js and leverages the CopilotKit SDK for a rich interactive experience.

## Tech Stack

* **Backend Agent**: Python, CrewAI, LiteLLM, Tavily API
* **Frontend UI**: Next.js, React, TypeScript, pnpm, CopilotKit SDK
* **LLM Access**: OpenRouter (for models like GPT-4o) or OpenAI directly (configurable in the agent)
* **Search**: Tavily

## Project Structure

The project is primarily divided into two main directories:

* `agent/`: Contains the Python-based CrewAI agent backend, including all logic for tools, prompts, and agent orchestration.
* `ui/`: Contains the Next.js frontend application that users interact with.

---

## Prerequisites

Before you begin, ensure your development environment includes:

* **Python**: Version 3.9 or higher is recommended.
* **Poetry**: For managing Python dependencies in the `agent-py` directory. If not installed, see the [Poetry Installation Guide](https://python-poetry.org/docs/#installation).
* **Node.js**: LTS version (e.g., 18.x, 20.x, or newer) is recommended.
* **pnpm**: For managing Node.js dependencies in the `ui` directory. If not installed, see the [pnpm Installation Guide](https://pnpm.io/installation).

---

## Setup and Installation

### 1. Clone Repository

If you haven't already, clone your project repository to your local machine:

```sh
git clone <your-repository-url>
cd <your-project-name> # Navigate to your project's root directory