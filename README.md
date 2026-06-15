# AI-Powered Document Classifier for Amazon Relay

## Overview
An intelligent document classification system built for Amazon Relay's identity verification workflow. Uses **Google Gemini AI** to automatically classify, extract fields, detect red flags, and route carrier documents — reducing manual review time by an estimated 80%.

## Problem Statement
Amazon Relay processes **2M+ carrier document investigations per year**. Each document must be:
1. Identified (what type is it?)
2. Verified (is the information valid?)
3. Routed (auto-approve, human review, or reject?)

This project automates all three steps using AI.

## Features

| Feature | Description |
|---------|-------------|
| AI Classification | Gemini 2.5 Flash identifies document type with 95%+ confidence |
| Field Extraction | Automatically pulls key data (names, IDs, dates, etc.) |
| Red Flag Detection | Catches expired documents, missing fields, inconsistencies |
| Smart Routing | Auto-approves high-confidence docs, flags uncertain ones for human review |
| Dual Engine | AI-powered (Gemini) + Rule-based (keyword matching) as fallback |
| History Tracking | Logs all classifications with performance metrics |

## Document Types Supported

- Driver's License
- Passport
- Insurance Certificate
- Compliance Form (FMCSA)
- Vehicle Registration

## Tech Stack

- **Frontend:** Streamlit
- **AI Engine:** Google Gemini 2.5 Flash
- **Language:** Python 3.x
- **Libraries:** Faker, Pandas, PyPDF2, python-dotenv
- **Data:** 50 synthetic documents (generated with Faker)

