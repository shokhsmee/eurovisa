eurovisa CRM System

Domain: https://eurovisa.uz

Author: Shohjahon Obruyev
Stack: Odoo 18/19 Community (Enterprise preferred)
Purpose: Custom CRM system with integrated IP-telephony, Finance, Telegram Bot, SMS Provider, and Employee Management.

Overview

The eurovisa CRM system is a fully integrated business process automation platform built on top of Odoo. It provides end-to-end workflow management for visa agencies and service companies.

Key features include:

Lead and Customer Management

IP Telephony Integration

Eskiz SMS Integration

Telegram Bot for Agents

Financial Tracking and Reporting

Employee Management and Performance Monitoring

Contact Center Tools

Authentication Customizations

Core Modules

Below are the primary Odoo add-ons included in this repository:

Module	Description
crm_apps	Base CRM extensions and adjustments
visa_agent_crm	Agent lead management, user access, lead assignments
moizvonki_calls	IP telephony integration via moizvonki API
crm_eskiz_sms	Eskiz SMS provider integration for notifications
visa_finance	Finance workflow, billing, payment tracking
contact	Contact and customer extensions
visa_agent_bot	Telegram bot integration for agents
login_viza	Custom login UX and styling
Features Overview
CRM and Sales

Lead creation from multiple input channels

Status stages and pipelines

Assignment rules for agents

Telegram bot lead notifications

IP Telephony Integration

Call logs from Asterisk/Moizvonki (via moizvonki_calls)

Employee call performance

Click-to-call optional support

Call recordings support (optional)

SMS Integration (Eskiz)

OTP and notification messages

Lead status alerts

Automated templates

Configuration via General Settings

Telegram Bot Integration

Agent notification system

Lead updates via bot

Authentication per-user

Finance Module

Deal payment flow

Revenue tracking

Finance summaries and dashboards

Employee Management

Employee call metrics

Agent performance summary

Access rights segmentation

System Architecture
Users/Agents -> CRM + Bot -> Finance -> SMS -> Telephony -> Employees
                       |           |
                       |           ----> Reports
                       |
                       ------> Dashboard

Installation
Prerequisites

Ubuntu 22.04 recommended

Python 3.11+

PostgreSQL 14+

Odoo 18 or Odoo 19 Community / Enterprise

wkhtmltopdf installed

Clone Repository
git clone git@github.com:shokhsmee/eurovisa.git
cd eurovisa

Install Python Dependencies
pip install -r requirements.txt


(or your virtualenv workflow)

Configure Odoo

Add custom addons path to odoo.conf:

addons_path = addons,custom-addons


Example layout:

odoo/
  odoo.conf
  custom-addons/
     crm_apps/
     visa_finance/
     visa_agent_crm/
     ...

Database Setup

Create database manually or via Odoo web UI.

Configuration Steps
1. Eskiz SMS Setup

Go to Settings > Technical > Eskiz Settings

Enter:

Email

Password

Token refresh interval

2. Moizvonki IP Telephony Setup

Go to Settings > Telephony

Configure:

API keys

Webhook URL

Recording access (optional)

Webhook endpoint example:

/moizvonki/webhook

3. Telegram Bot Setup

Configure in:

Settings > Integrations > Telegram Bot

Parameters:

Bot Token

Allowed Users

Message Templates

4. Finance Module Configuration

Enable in:

Finance > Settings

Running the System

From terminal:

./odoo-bin -c odoo.conf


or with systemd service.

Images and Screenshots (Add later)

Place screenshots under docs/images/ or similar.

Recommended sections:

Dashboard View

<img width="1905" height="981" alt="image" src="https://github.com/user-attachments/assets/7a185253-a0db-4486-9994-cfd11783607e" />

CRM Lead Pipeline

<img width="1919" height="991" alt="image" src="https://github.com/user-attachments/assets/1160c434-5e3e-4128-a017-153cede66383" />

Finance Summary

<img width="1919" height="987" alt="image" src="https://github.com/user-attachments/assets/7842650b-b89e-4026-853a-3d2e8fe0785b" />

Telegram Bot Workflow

<img width="1179" height="2556" alt="image" src="https://github.com/user-attachments/assets/c0323215-0755-4a51-bb3f-3d0cfbbdfc71" />

Add them like:

<img width="1919" height="988" alt="image" src="https://github.com/user-attachments/assets/38508f0d-9a7e-4200-b072-c0249969a9d0" />
<img width="1919" height="988" alt="image" src="https://github.com/user-attachments/assets/8a826171-a360-44df-8b63-422494c260e6" />
<img width="1919" height="991" alt="image" src="https://github.com/user-attachments/assets/16e7d358-40fc-423b-a4b3-7111f36ef6ec" />
<img width="1919" height="987" alt="image" src="https://github.com/user-attachments/assets/f9dbd062-4d40-4c61-9805-828950572fff" />


Tech Stack
Component	Version
Python	3.11+
Odoo	18/19
PostgreSQL	14+
Telegram Bot API	Yes
Eskiz SMS API	Yes
Moizvonki API	Yes
Deployment Notes

For production:

Use reverse proxy (NGINX)

Use SSL (LetsEncrypt recommended)

Use workers for scaling

Use PostgreSQL tuning for performance

Use logging for telephony + bot debugging

Future Improvements (Roadmap)

Call recording storage cleanup

Finance reconciliation

Agent KPI dashboards

Twilio optional support

Multi-company support

License

Proprietary use, internal deployment only unless specified by author.
