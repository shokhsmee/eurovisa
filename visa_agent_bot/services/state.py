# -*- coding: utf-8 -*-
from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    phone = State()
    name = State()
    department = State()
    email = State()
    job_position = State()

class AgentWork(StatesGroup):
    """States for agent working with CRM"""
    waiting_taklifnoma = State()  # Waiting for document upload