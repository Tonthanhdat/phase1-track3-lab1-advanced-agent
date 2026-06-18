from __future__ import annotations
from .schemas import QAExample, JudgeResult, ReflectionEntry
from .utils import normalize_answer

import json
import time
import os
from dotenv import load_dotenv
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM

load_dotenv()

FAILURE_MODE_BY_QID = {"hp2": "incomplete_multi_hop", "hp4": "wrong_final_answer", "hp6": "entity_drift", "hp8": "entity_drift"}

class LLMTracker:
    total_tokens = 0
    total_latency = 0
    
    @classmethod
    def reset(cls):
        cls.total_tokens = 0
        cls.total_latency = 0

def call_llm(system_prompt: str, user_prompt: str, response_schema=None) -> str:
    start_time = time.time()
    try:
        from openai import OpenAI
        client = OpenAI()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {
            "model": "gpt-4o-mini",
            "messages": messages,
        }
        
        if response_schema:
            kwargs["response_format"] = {"type": "json_object"}
            
        response = client.chat.completions.create(**kwargs)
        
        latency = int((time.time() - start_time) * 1000)
        tokens = response.usage.total_tokens if response.usage else 0
        LLMTracker.total_latency += latency
        LLMTracker.total_tokens += tokens
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM Error: {e}")
        LLMTracker.total_latency += int((time.time() - start_time) * 1000)
        return ""

def actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> str:
    context_str = "\n".join([f"[{c.title}] {c.text}" for c in example.context])
    user_prompt = f"Question: {example.question}\n\nContext:\n{context_str}"
    if reflection_memory:
        user_prompt += "\n\nPast failed attempts and lessons:\n" + "\n".join(reflection_memory)
    return call_llm(ACTOR_SYSTEM, user_prompt).strip()

def evaluator(example: QAExample, answer: str) -> JudgeResult:
    if normalize_answer(example.gold_answer) == normalize_answer(answer):
        return JudgeResult(score=1, reason="Final answer matches the gold answer after normalization.", failure_mode="none")
    
    user_prompt = f"Question: {example.question}\nGold Answer: {example.gold_answer}\nPredicted Answer: {answer}"
    res = call_llm(EVALUATOR_SYSTEM, user_prompt, response_schema=JudgeResult)
    try:
        data = json.loads(res)
        return JudgeResult(**data)
    except Exception:
        return JudgeResult(score=0, reason="Failed to evaluate", failure_mode="wrong_final_answer")

def reflector(example: QAExample, attempt_id: int, judge: JudgeResult) -> ReflectionEntry:
    context_str = "\n".join([f"[{c.title}] {c.text}" for c in example.context])
    user_prompt = f"Question: {example.question}\nContext:\n{context_str}\nFailed Reason: {judge.reason}"
    res = call_llm(REFLECTOR_SYSTEM, user_prompt, response_schema=ReflectionEntry)
    try:
        data = json.loads(res)
        data["attempt_id"] = attempt_id
        return ReflectionEntry(**data)
    except Exception:
        return ReflectionEntry(attempt_id=attempt_id, failure_reason=judge.reason, lesson="Error", next_strategy="Try again.")

